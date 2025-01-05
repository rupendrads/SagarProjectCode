# # -*- coding: utf-8 -*-
# """
# Created on Thu Aug 22 23:38:49 2024

# @author: Admin
# """
# import time
# import os
# import json
# import sys
# from flask import Flask, request, jsonify
# from flask_cors import CORS # type: ignore
# import mysql
# try:
#     from index_data_upload_latest import DataProcessor, initialize_log_file, db_config, IndexCreator, log_action
# except ImportError as e:
#     print(f"Error importing DataProcessor: {e}")

# try:
#     from gdfl_implied_futures import ImpliedFuturesCalculator, db_config
# except ImportError as e:
#     print(f"Error importing DataProcessor: {e}")
    
# from constants import db_config,db_name
    
# app = Flask(__name__)
# CORS(app)

# @app.route('/processdata', methods=['POST'])
# def get_strategy_name():

#    value = None
#    data = request.json
#    upload_status = data['force_upload']['forceUpload']
#    print(f' data :{data}')
#    data = data['filePath']
#    data = data.replace('/','\\')
#    data = data.replace('\\', '\\\\')
#    print(f'upload_status {upload_status}')
#    data = {'filepath': data,'force_upload': upload_status}
#    print(type(data))
#    print(f' data :{data}')
#         # Check if the input is a dictionary
#    if not isinstance(data, dict):
#        return jsonify({'status': 'error', 'message': 'Expected a dictionary'}), 400

#         # Initialize necessary components
#    initialize_log_file()
    
#    connection = mysql.connector.connect(**db_config)
#    cursor = connection.cursor()
#    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
#    cursor.close()
#    connection.close()
   
#    db_config['database'] = db_name
#    directory_paths = [
#         r'D:\Rupendra\Work\Sagar\uploadGDFL\GFDLNFO_BACKADJUSTED_07062023.csv',
#     ]
#    print(directory_paths)
#        # Instantiate DataProcessor
#    index_processor = DataProcessor(directory_paths, db_config)
   

# #    index_creator.delete_indices()
#         # Extract filename and force_upload from the dictionary
#    print(f"data is {data}")
#    filename = data.get('filepath')
#    force_upload = data.get('force_upload')
#    print(f"data {data}")  
   
#    print(f"Processing file: {filename} with force_upload={force_upload}")
   
   
#     # Call preprocess_data for the file
#    value,status = index_processor.preprocess_data(filename, force_upload)
    
#     # Instantiate IndexCreator and perform indexing
#    log_action(f"Creating indices for {filename}")
# #    index_creator = IndexCreator(db_config)
# #    index_creator.connect_to_database()
# #    index_creator.create_indices()
# #    log_action(f"finished Creating indices for {filename}")
# #    index_creator.close_database_connection()
#    if status == 'success':
#     # Return failure response if the status is 'error'
#         return jsonify({'Status': 'success', 'Details': value}), 200        
#    else:
#         # Return success response if the status is 'success'
#         return jsonify({'Status': 'error', 'Details': value}), 500
        

# @app.route('/upload/impliedfutures', methods=['POST'])
# def upload_implied_futures():
#    value = None
#    data = request.json
#    instrument_name = data.get('instrument_name')
#    start_date = data.get('start_date')
#    end_date = data.get('end_date')
#    strike_difference = data.get('strike_difference')
#    if not all([instrument_name, start_date, end_date, strike_difference]):
#         return jsonify({'error': 'Missing parameters'}), 400

#     # Instantiate ImpliedFuturesCalculator with parameters
#    calculator = ImpliedFuturesCalculator(instrument_name, start_date, end_date, strike_difference)
#    value = calculator.run()
#    print(f"value in server")
#    print({"Status":'success'})
#    if value == "true":
#        return jsonify({'Status': 'success'}), 200  
#    else:
#        return jsonify({'Status': 'error'}), 500  

     
    
# if __name__ == '__main__':
#     app.run()

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 23:38:49 2024

@author: Admin
"""
import time
import os
import json
import re
import sys
from pydantic import BaseModel
from typing import List, Set
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import Error 
try:
    from index_data_upload_latest import DataProcessor, initialize_log_file, db_config, IndexCreator, log_action
except ImportError as e:
    print(f"Error importing DataProcessor: {e}")

try:
    from gdfl_implied_futures import ImpliedFuturesCalculator, db_config
except ImportError as e:
    print(f"Error importing ImpliedFuturesCalculator: {e}")

#from constants import db_config, db_name

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current script
    sagar_common_path = os.path.join(current_dir, "../../Sagar_common")  # Go up two levels to "OGCODE"
    if sagar_common_path not in sys.path:
        sys.path.append(sagar_common_path)
    from common_function import fetch_parameter
except ImportError as e:
    print(f"Errorfetching db details: {e}")

app = FastAPI()

app.add_middleware( 
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = "dev"  # Environment, e.g., 'dev', 'prod'
key = "db_index_data"  # Example key
db_Value = fetch_parameter(env, key)
if db_Value is None:
    raise HTTPException(status_code=500, detail="Failed to fetch database configuration.")
print(f"Fetched db config: {db_Value}")

@app.post('/processdata')
async def get_strategy_name(request: Request):
    env = "dev"  # Set the environment (e.g., 'dev', 'prod')
    key = "db_upload"  # Example key used to fetch configuration
    db_Value = fetch_parameter(env, key)  # Fetch the database configuration

    # Ensure db_Value is correctly fetched before using it
    if not db_Value:
        raise HTTPException(status_code=500, detail="Failed to fetch database configuration.")

    data = await request.json()
    upload_status = data['force_upload']['forceUpload']
    print(f'data: {data}')
    
    data_path = data['filePath']
    data_path = data_path.replace('/', '\\')
    data = {'filepath': data_path, 'force_upload': upload_status}

    print(f'Processed data: {data}')
    
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Expected a dictionary")

    # Initialize log file
    initialize_log_file()

    # Create a MySQL database connection using db_Value
    try:
        connection = mysql.connector.connect(**db_Value)
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_Value['database']}")
        cursor.close()
        connection.close()
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")

    #db_Value['database'] = db_name  # Update db_Value to include the db_name
    directory_paths = [
        r'D:\Rupendra\Work\Sagar\uploadGDFL\GFDLNFO_BACKADJUSTED_07062023.csv',
    ]
    print(f"Directory paths: {directory_paths}")

    # Initialize DataProcessor with the directory paths and database config
    index_processor = DataProcessor(directory_paths, db_Value)

    print(f"data: {data}")
    filename = data.get('filepath')
    force_upload = data.get('force_upload')
    print(f"Processing file: {filename} with force_upload={force_upload}")

    # Call preprocess_data to process the file
    value, status = index_processor.preprocess_data(filename, force_upload)

    log_action(f"Creating indices for {filename}")

    # Return appropriate response based on the status of the processing
    if status == 'success':
        return JSONResponse(content={'Status': 'success', 'Details': value}, status_code=200)
    else:
        return JSONResponse(content={'Status': 'error', 'Details': value}, status_code=500)

@app.post('/upload/impliedfutures')
async def upload_implied_futures(request: Request):
    data = await request.json()
    instrument_name = data.get('instrument_name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    strike_difference = data.get('strike_difference')

    if not all([instrument_name, start_date, end_date, strike_difference]):
        raise HTTPException(status_code=400, detail="Missing parameters")

    calculator = ImpliedFuturesCalculator(instrument_name, start_date, end_date, strike_difference)
    value = calculator.run()
    print(f"value in server")
    print({"Status": 'success'})

    if value == "true":
        return JSONResponse(content={'Status': 'success'}, status_code=200)
    else:
        return JSONResponse(content={'Status': 'error'}, status_code=500)
def get_db_connection():
    """
    Establish a connection to the MySQL database.
    Returns the connection object or None if connection fails.
    """
    try:
        # Make sure 'value' is properly initialized before use
        if not db_Value:
            raise HTTPException(status_code=500, detail="Database configuration is missing.")
        
        connection = mysql.connector.connect(
            host=db_Value['host'],
            user=db_Value['user'],
            password=db_Value['password'],
            database=db_Value['database']
        )
        return connection
    except mysql.Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise HTTPException(status_code=500, detail="Database connection error.")

TABLE_PATTERN = re.compile(r".*_(\d{4}|fut)$")

class FileNames(BaseModel):
    filenames: List[str]

def extract_unique_years(filenames: List[str]) -> Set[str]:
    """
    Extract unique 4-digit years from the provided filenames.
    """
    years = set()
    for filename in filenames:
        match = re.search(r"(\d{4})\.csv$", filename)
        if match:
            years.add(match.group(1))
    return years

def get_matching_tables(years: Set[str], tables: set) -> List[str]:
    """
    Retrieve a list of tables from the database that match the given years
    or end with '_fut'.
    """
    target_tables = []
    for year in years:
        matched_tables = [t for t in tables if t.endswith(f"_{year}") or t.endswith("_fut")]
        if not matched_tables:
            print(f"No tables found for year: {year}")
        target_tables.extend(matched_tables)
    return target_tables

def get_existing_indices(cursor, table_name):
    """
    Retrieve existing indices for a given table.
    """
    cursor.execute(f"SHOW INDEX FROM {table_name}")
    indices = cursor.fetchall()
    existing_indices = set(index[2] for index in indices)
    return existing_indices


def read_filenames_from_json():
    try:
        with open("files.json", "r") as json_file:
            data = json.load(json_file)
            return data.get("filenames", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading from files.json: {e}")
        return []
    
    
@app.post("/create-indices")
def create_indices():
    """
    Create indices on 'timestamp', 'symbol', and 'type' columns for tables
    corresponding to the years extracted from the filenames stored in 'files.json'.
    If an index already exists, it is skipped.
    Returns a status indicating success or failure.
    """
    print("create indices being called")

    filenames = read_filenames_from_json()
    print(filenames)
    if not filenames:
        print("No filenames found in files.json.")
        return {"status": "failed"}

    connection = get_db_connection()
    if connection is None:
        return {"status": "failed"}

    errors_occurred = False
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = {table_name[0] for table_name in cursor.fetchall()}

        years = extract_unique_years(filenames)
        if not years:
            print("No valid years extracted from filenames.")
            errors_occurred = True
            return {"status": "failed"}

        target_tables = get_matching_tables(years, tables)
        if not target_tables:
            print("No matching tables found for the provided years.")
            errors_occurred = True
            return {"status": "failed"}

        for table_name in target_tables:
            try:
                existing_indices = get_existing_indices(cursor, table_name)

                timestamp_index = f"idx_{table_name}_timestamp"
                symbol_index = f"idx_{table_name}_symbol"
                type_index = f"idx_{table_name}_type"

                if timestamp_index not in existing_indices:
                    cursor.execute(f"CREATE INDEX {timestamp_index} ON {table_name} (timestamp)")
                    print(f"Index {timestamp_index} created on {table_name}.")
                else:
                    print(f"Index {timestamp_index} already exists on {table_name}, skipping.")

                if symbol_index not in existing_indices:
                    cursor.execute(f"CREATE INDEX {symbol_index} ON {table_name} (symbol)")
                    print(f"Index {symbol_index} created on {table_name}.")
                else:
                    print(f"Index {symbol_index} already exists on {table_name}, skipping.")

                if type_index not in existing_indices:
                    cursor.execute(f"CREATE INDEX {type_index} ON {table_name} (type)")
                    print(f"Index {type_index} created on {table_name}.")
                else:
                    print(f"Index {type_index} already exists on {table_name}, skipping.")

            except Error as e:
                print(f"Error creating indices on table {table_name}: {e}")
                errors_occurred = True

        connection.commit()
        cursor.close()
        connection.close()
        
        return {"status": "success" if not errors_occurred else "partial success"}
    except Error as e:
        print(f"Unexpected error: {e}")
        return {"status": "failed"}

@app.delete("/delete-indices")
def delete_indices(file_data: FileNames):
    """
    Delete indices on 'timestamp', 'symbol', and 'type' columns for tables
    corresponding to the years extracted from the provided filenames.
    If an index does not exist, it is skipped.
    Returns a status indicating success or failure.
    """
    print("delete indices being called")
    with open("files.json", "w") as json_file:
        json.dump({"filenames": file_data.filenames}, json_file)
        print("Filenames saved to files.json")
    connection = get_db_connection()
    if connection is None:
        return {"status": "failed"}

    errors_occurred = False
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = {table_name[0] for table_name in cursor.fetchall()}

        years = extract_unique_years(file_data.filenames)
        if not years:
            print("No valid years extracted from filenames.")
            errors_occurred = True
            return {"status": "failed"}

        target_tables = get_matching_tables(years, tables)
        if not target_tables:
            print("No matching tables found for the provided years.")
            errors_occurred = True
            return {"status": "failed"}

        for table_name in target_tables:
            try:
                existing_indices = get_existing_indices(cursor, table_name)

                timestamp_index = f"idx_{table_name}_timestamp"
                symbol_index = f"idx_{table_name}_symbol"
                type_index = f"idx_{table_name}_type"

                if timestamp_index in existing_indices:
                    cursor.execute(f"DROP INDEX {timestamp_index} ON {table_name}")
                    print(f"Index {timestamp_index} deleted from {table_name}.")
                else:
                    print(f"Index {timestamp_index} does not exist on {table_name}, skipping.")

                if symbol_index in existing_indices:
                    cursor.execute(f"DROP INDEX {symbol_index} ON {table_name}")
                    print(f"Index {symbol_index} deleted from {table_name}.")
                else:
                    print(f"Index {symbol_index} does not exist on {table_name}, skipping.")

                if type_index in existing_indices:
                    cursor.execute(f"DROP INDEX {type_index} ON {table_name}")
                    print(f"Index {type_index} deleted from {table_name}.")
                else:
                    print(f"Index {type_index} does not exist on {table_name}, skipping.")

            except Error as e:
                print(f"Error deleting indices on table {table_name}: {e}")
                errors_occurred = True

        connection.commit()
        cursor.close()
        connection.close()

    except Error as e:
        print(f"Database error: {e}")
        errors_occurred = True

    if errors_occurred:
        return {"status": "failed"}
    else:
        return {"status": "success"}
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=9000)

