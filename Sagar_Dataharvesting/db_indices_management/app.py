from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Set
import mysql.connector
from mysql.connector import Error
from constants import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST
import re

app = FastAPI()

def get_db_connection():
    """
    Establish a connection to the MySQL database.
    Returns the connection object or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

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

@app.post("/create-indices")
def create_indices(file_data: FileNames):
    """
    Create indices on 'timestamp', 'symbol', and 'type' columns for tables
    corresponding to the years extracted from the provided filenames.
    If an index already exists, it is skipped.
    Returns a status indicating success or failure.
    """
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

    except Error as e:
        print(f"Database error: {e}")
        errors_occurred = True

    if errors_occurred:
        return {"status": "failed"}
    else:
        return {"status": "success"}

@app.delete("/delete-indices")
def delete_indices(file_data: FileNames):
    """
    Delete indices on 'timestamp', 'symbol', and 'type' columns for tables
    corresponding to the years extracted from the provided filenames.
    If an index does not exist, it is skipped.
    Returns a status indicating success or failure.
    """
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
