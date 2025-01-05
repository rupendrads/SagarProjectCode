from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
import os
import pandas as pd
import mysql.connector
import re
import logging
from datetime import datetime
import shutil
import csv
from typing import Dict, List, Set
from constants import db_creds
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('app.log')
console_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = FastAPI()

class FolderPath(BaseModel):
    folderPath: str

# Function to log queries to query.txt
def log_query(query: str):
    with open('query.txt', 'a') as query_file:
        query_file.write(f"{query}\n")

@app.get("/process_folder")
async def process_folder(folder_path: FolderPath = Body(...)) -> Dict[str, str]:
    folder_path_str: str = folder_path.folderPath

    if not os.path.exists(folder_path_str):
        logger.error(f"Folder path {folder_path_str} does not exist.")
        raise HTTPException(status_code=400, detail="Folder path does not exist.")

    filenames: List[str] = [f for f in os.listdir(folder_path_str) if f.startswith('GFDLNFO_BACKADJUSTED') and f.endswith('.csv')]

    file_date_dict: Dict[str, str] = {}
    date_pattern = re.compile(r'GFDLNFO_BACKADJUSTED_(\d{8})\.csv')
    for filename in filenames:
        match = date_pattern.match(filename)
        if match:
            date_str: str = match.group(1)
            file_date_dict[filename] = date_str
        else:
            logger.warning(f"Filename {filename} does not match expected pattern.")

    if not os.path.exists('database_tables.csv'):
        try:
            connection = mysql.connector.connect(
                host=db_creds['host'],
                database=db_creds['database'],
                user=db_creds['user'],
                password=db_creds['password']
            )

            if connection.is_connected():
                cursor = connection.cursor()
                # Log and execute the query
                show_tables_query = "SHOW TABLES;"
                log_query(show_tables_query)
                cursor.execute(show_tables_query)
                tables = cursor.fetchall()

                pattern_year = re.compile(r'.*_\d{4}$')
                pattern_fut = re.compile(r'.*_fut$')

                filtered_tables: List[str] = [table[0] for table in tables if pattern_year.match(table[0]) or pattern_fut.match(table[0])]

                with open('database_tables.csv', mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['tables'])
                    for table in filtered_tables:
                        writer.writerow([table])

                logger.info("database_tables.csv has been successfully created.")
        except mysql.connector.Error as e:
            logger.error(f"Error while fetching table names: {e}")
            raise HTTPException(status_code=500, detail="Error while fetching table names from database.")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                logger.info("MySQL connection closed.")
    else:
        logger.info("database_tables.csv already exists.")

    database_tables_df = pd.read_csv('database_tables.csv')
    database_tables: List[str] = database_tables_df['tables'].tolist()

    years: Set[str] = set()
    pattern_year = re.compile(r'.*_(\d{4})$')
    for table_name in database_tables:
        match = pattern_year.match(table_name)
        if match:
            year: str = match.group(1)
            years.add(year)

    discrepancy_folder: str = os.path.join(folder_path_str, 'discrepancy')
    processed_folder: str = os.path.join(folder_path_str, 'processed_files')
    os.makedirs(discrepancy_folder, exist_ok=True)
    os.makedirs(processed_folder, exist_ok=True)

    with open('discrepancy.txt', 'a') as discrepancy_file:
        for filename, date_str in file_date_dict.items():
            try:
                date_obj = datetime.strptime(date_str, '%d%m%Y')
                date_formatted: str = date_obj.strftime('%Y-%m-%d')
                year: str = date_obj.strftime('%Y')
            except ValueError as e:
                logger.error(f"Invalid date format in filename {filename}: {e}")
                discrepancy_file.write(f"{filename}, Invalid date format: {e}\n")
                continue

            if year not in years:
                logger.warning(f"No tables for year {year} in database.")
                discrepancy_file.write(f"{filename}, No tables for year {year} in database\n")
                continue

            pattern_year_specific = re.compile(rf'.*_{year}$')
            pattern_fut = re.compile(r'.*_fut$')
            filtered_tables = [table for table in database_tables if pattern_year_specific.match(table) or pattern_fut.match(table)]
            
            if not filtered_tables:
                logger.warning(f"No tables found for date {date_formatted}")
                discrepancy_file.write(f"{filename}, No tables found for date {date_formatted}\n")
                continue

            query_parts: List[str] = []
            for table in filtered_tables:
                query_part = f"SELECT timestamp FROM {db_creds['database']}.{table} WHERE DATE(timestamp) = '{date_formatted}'"
                query_parts.append(query_part)

            combined_query = " UNION ALL\n".join(query_parts)
            final_query = f"SELECT COUNT(*) AS total_count\nFROM (\n{combined_query}\n) AS combined_tables;"

            # Log and execute the query
            log_query(final_query)

            db_count = None
            try:
                connection = mysql.connector.connect(
                    host='localhost',
                    database=db_creds['database'],
                    user='root',
                    password='pegasus'
                )

                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute(final_query)
                    db_count = cursor.fetchone()[0]
                    logger.info(f"Database count for date {date_formatted}: {db_count}")
            except mysql.connector.Error as e:
                logger.error(f"Error executing query for date {date_formatted}: {e}")
                discrepancy_file.write(f"{filename}, Query error: {e}\n")
                continue
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

            file_path = os.path.join(folder_path_str, filename)
            try:
                df = pd.read_csv(file_path)
                file_count: int = len(df)
                logger.info(f"File count for {filename}: {file_count}")
            except Exception as e:
                logger.error(f"Error reading file {filename}: {e}")
                discrepancy_file.write(f"{filename}, Read error: {e}\n")
                continue

            file_in_status = False
            try:
                connection = mysql.connector.connect(
                    host='localhost',
                    database=db_creds['database'],
                    user='root',
                    password='pegasus'
                )

                if connection.is_connected():
                    cursor = connection.cursor(dictionary=True)
                    upload_status_query = f"""
                        SELECT * FROM {db_creds['database']}.upload_status
                        WHERE file_name = '{filename}' AND status = '1'
                        ORDER BY upload_time DESC LIMIT 1;
                    """
                    # Log and execute the query
                    log_query(upload_status_query)
                    cursor.execute(upload_status_query)
                    file_in_status = cursor.fetchone() is not None
            except mysql.connector.Error as e:
                logger.error(f"Error checking upload_status for file {filename}: {e}")
                discrepancy_file.write(f"{filename}, Status check error: {e}\n")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

            # Check if counts match or not, and handle accordingly
            if db_count == file_count:
                # Move file to processed folder if counts match
                shutil.move(file_path, os.path.join(processed_folder, filename))
                logger.info(f"Moved file {filename} to processed_files.")
            else:
                # Log the discrepancy, move file to discrepancy folder
                file_status = "exists" if file_in_status else "does not exist"
                discrepancy_message = f"{filename}, Database count: {db_count}, File count: {file_count}, Status: {file_status}, Counts didn't match\n"
                discrepancy_file.write(discrepancy_message)
                shutil.move(file_path, os.path.join(discrepancy_folder, filename))
                logger.info(f"Moved file {filename} to discrepancy folder.")

    return {"message": "Processing completed. Check logs and folders for details."}
