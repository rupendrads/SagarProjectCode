import mysql.connector
import re
import os
import pandas as pd
import json
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Existing logger for general logs
logging.basicConfig(filename='file_verification.txt',
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a new logger for processing files
processing_logger = logging.getLogger('processing_logger')
processing_logger.setLevel(logging.INFO)
processing_handler = logging.FileHandler('processing_files.txt')
processing_handler.setLevel(logging.INFO)
processing_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
processing_handler.setFormatter(processing_formatter)
processing_logger.addHandler(processing_handler)

# Create a new logger for discrepancy logs
discrepancy_logger = logging.getLogger('discrepancy_logger')
discrepancy_logger.setLevel(logging.INFO)
discrepancy_handler = logging.FileHandler('discrepancy_log.txt')
discrepancy_handler.setLevel(logging.INFO)
discrepancy_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
discrepancy_handler.setFormatter(discrepancy_formatter)
discrepancy_logger.addHandler(discrepancy_handler)

class ValidateDbDataResponse(BaseModel):
    status: bool
    message: Optional[str] = None
    file_results: List[dict] = []

class FolderPathRequest(BaseModel):
    folderPath: str

app = FastAPI()

# Database connection function
def connect_to_db(host: str, user: str, password: str, database: str) -> mysql.connector.connection.MySQLConnection:
    try:
        conn = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        if conn.is_connected():
            print("Connected to database.")
            return conn
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

# Get files from the database
def get_files_from_db(conn: mysql.connector.connection.MySQLConnection) -> set:
    try:
        cursor = conn.cursor()
        query = "SELECT file_name FROM upload_status WHERE status = 1"
        cursor.execute(query)
        rows = cursor.fetchall()
        return set(row[0] for row in rows)
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        if cursor:
            cursor.close()

# Check upload count in the database
def check_upload_count(file_name: str, conn: mysql.connector.connection.MySQLConnection):
    try:
        cursor = conn.cursor()
        query = """
            SELECT upload_count 
            FROM upload_status 
            WHERE file_name=%s 
            AND STATUS=1
            ORDER BY upload_time DESC 
            LIMIT 1
        """
        cursor.execute(query, (file_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.errors.InternalError as e:
        print(f"Error fetching upload count: {e}")
    finally:
        if cursor:
            cursor.close()

# Get filtered table names based on the year
def get_filtered_table_names(year: str, conn: mysql.connector.connection.MySQLConnection):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    filtered_tables = [table[0] for table in tables if table[0].endswith((year, '_fut'))]
    cursor.close()
    return filtered_tables

# Extract year from filename
def extract_year_from_filename(filename: str):
    base_filename = filename.split('.csv')[0]
    match = re.search(r'(\d{4}$)', base_filename)
    return match.group(0) if match else None

# Count providers in tables for a specific file
def count_provider_in_tables(filename: str, conn: mysql.connector.connection.MySQLConnection):
    year = extract_year_from_filename(filename)
    if not year:
        print("Invalid filename format, unable to extract year.")
        return 0

    filtered_tables = get_filtered_table_names(year, conn)
    total_count = 0

    cursor = conn.cursor()

    for table in filtered_tables:
        try:
            query = f"SELECT COUNT(*) FROM {table} WHERE provider = %s"
            cursor.execute(query, (filename,))
            result = cursor.fetchone()
            if result:
                count = result[0]
                print(f"Count in {table}: {count} for {filename}")
                total_count += count
        except mysql.connector.Error as err:
            print(f"Error querying {table}: {err}")

    cursor.close()
    print(f"total count of {filename} is {total_count}")
    return total_count

def process_file(filename: str, folder_path: str, db_params: dict):
    # Log before processing the file
    processing_logger.info(f"Processing file: {filename}")

    file_results = []
    discrepancies_found = False
    conn = connect_to_db(**db_params)

    # Check if the file is present in the upload_status table
    uploaded_data = check_upload_count(filename, conn)
    if uploaded_data is None:
        file_status = False
        file_message = 'File is not uploaded in DB'
        discrepancies_found = True
        result = {
            'filename': filename,
            'status': file_status,
            'message': file_message,
            'csv_count': None,
            'total_count': None,
            'db_count': None
        }
        discrepancy_logger.info(f"File: {filename}, Status: {file_status}, Message: {file_message}")
        file_results.append(result)
        conn.close()
        return file_results, discrepancies_found

    # Proceed to count checks if the file is uploaded
    file_path = os.path.join(folder_path, filename)
    data = pd.read_csv(file_path)
    csv_count = data.shape[0]

    total_count = count_provider_in_tables(filename, conn)

    if csv_count != total_count:
        file_status = False
        file_message = 'Discrepancy between CSV count and total count'
        discrepancies_found = True
    elif total_count != uploaded_data:
        file_status = False
        file_message = 'Discrepancy between total count and DB records'
        discrepancies_found = True
    else:
        file_status = True
        file_message = 'Database records match File records'

    result = {
        'filename': filename,
        'status': file_status,
        'message': file_message,
        'csv_count': csv_count,
        'total_count': total_count,
        'db_count': uploaded_data
    }

    # Log the discrepancies and counts
    discrepancy_logger.info(f"File: {filename}, Status: {file_status}, Message: {file_message}, CSV Count: {csv_count}, Total Count: {total_count}, DB Count: {uploaded_data}")

    file_results.append(result)

    conn.close()
    return file_results, discrepancies_found

@app.get("/validatedbdata", response_model=ValidateDbDataResponse)
async def validatedbdata(
    folder_request: FolderPathRequest,
    db_host: str = Query(..., alias="db_host"),
    db_user: str = Query(..., alias="db_user"),
    db_password: str = Query(..., alias="db_password"),
    db_name: str = Query(..., alias="db_name")
) -> ValidateDbDataResponse:
    db_params = {
        "host": db_host,
        "user": db_user,
        "password": db_password,
        "database": db_name
    }
    folder_path = folder_request.folderPath

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return ValidateDbDataResponse(status=False, message=f"Folder not found or is not a directory: {folder_path}")

    folder_files = set([filename for filename in os.listdir(folder_path) if filename.endswith('.csv')])
    conn = connect_to_db(**db_params)
    db_files = get_files_from_db(conn)
    conn.close()

    file_results = []
    discrepancies_found = False
    files_to_process = []

    for filename in folder_files:
        if filename not in db_files:
            result = {
                'filename': filename,
                'status': False,
                'message': 'File is not uploaded in DB',
                'csv_count': None,
                'total_count': None,
                'db_count': None
            }
            file_results.append(result)
            discrepancies_found = True
            discrepancy_logger.info(f"File: {filename}, Status: False, Message: File is not uploaded in DB")
        else:
            files_to_process.append(filename)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_file, filename, folder_path, db_params): filename for filename in files_to_process}
        
        for future in as_completed(futures):
            result, discrepancy = future.result()
            file_results.extend(result)
            if discrepancy:
                discrepancies_found = True

    missing_files = db_files - folder_files
    with open('missing_dates.txt', 'w') as file:
        for x in sorted(missing_files):
            file.write(f"{x}\n")
    conn = connect_to_db(**db_params)
    for missing_file in missing_files:
        db_count = check_upload_count(missing_file, conn)
        result = {
            'filename': missing_file,
            'status': False,
            'message': 'File is uploaded in DB but missing from folder',
            'csv_count': None,
            'total_count': None,
            'db_count': db_count
        }
        file_results.append(result)
        discrepancies_found = True
        discrepancy_logger.info(f"File: {missing_file}, Status: False, Message: File is uploaded in DB but missing from folder")
    conn.close()

    json_file = 'file_results.json'
    with open(json_file, 'w') as json_out:
        json.dump(file_results, json_out, indent=4)

    if not discrepancies_found:
        return ValidateDbDataResponse(
            status=True,
            message="All files in the folder are matched with the database",
            file_results=file_results
        )
    else:
        return ValidateDbDataResponse(
            status=False,
            message="Discrepancies found in the folder processing",
            file_results=file_results
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8081)
