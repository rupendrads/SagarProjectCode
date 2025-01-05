from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json  # Import json to handle JSON data
#from constants import db_credentials

app = FastAPI()

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current script
    sagar_common_path = os.path.join(current_dir, "../../../Sagar_common")  # Go up two levels to "OGCODE"
    if sagar_common_path not in sys.path:
        sys.path.append(sagar_common_path)
    from common_function import fetch_parameter
except ImportError as e:
    print(f"Error fetching db details: {e}")
    raise HTTPException(status_code=500, detail="Failed to import common functions.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

def connect_to_db() -> mysql.connector.connection.MySQLConnection:
    # Environment and key setup for fetching DB configuration
    env = "dev"  # Environment (e.g., 'dev', 'prod')
    key = "db_sagar_strategy"  # Key for fetching database details

    # Fetch database configuration from external source (e.g., a config file or service)
    db_Value = fetch_parameter(env, key)
    if db_Value is None:
        raise HTTPException(status_code=500, detail="Failed to fetch database configuration.")
    
    print(f"Fetched db config: {db_Value}")
    
    # Extract db credentials from the fetched configuration
    db_credentials = {
        "host": db_Value["host"],
        "database": db_Value["database"],
        "user": db_Value["user"],
        "password": db_Value["password"]
    }
    
    try:
        # Establishing the MySQL connection using the fetched credentials
        conn = mysql.connector.connect(
            host=db_credentials['host'],
            database=db_credentials['database'],
            user=db_credentials['user'],
            password=db_credentials['password']
        )
        
        if conn.is_connected():
            print("Connected to database.")
            return conn

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")


class KeyRequest(BaseModel):
    optimization_key: str

def get_optimization(optimization_key: str, conn: mysql.connector.connection.MySQLConnection):
    if conn:
        try:
            cursor = conn.cursor(buffered=True)
            query = """
                SELECT op_id, full_json 
                FROM optimisation
                WHERE optimization_key = %s
            """
            cursor.execute(query, (optimization_key,))
            result = cursor.fetchone()
            return result
        except mysql.connector.Error as e:
            print(f"Error fetching optimization: {e}")
        finally:
            if cursor:
                cursor.close()
    return None

def get_optimization_details(op_id: int, conn: mysql.connector.connection.MySQLConnection):
    if conn:
        try:
            cursor = conn.cursor(buffered=True)
            query = """
                SELECT id, status, combination_parameter, response_result 
                FROM optimisation_details
                WHERE op_id = %s
                ORDER BY id ASC
            """
            cursor.execute(query, (op_id,))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as e:
            print(f"Error fetching optimization details: {e}")
        finally:
            if cursor:
                cursor.close()
    return []


@app.post("/retryOptimization")
async def getallcombinations(key_request: KeyRequest):
    key_value = key_request.optimization_key
    print(f"optimization key is {key_value}")
    conn = None
    try:
        conn = connect_to_db()
        
        result = get_optimization(key_value, conn)
        if not result:
            raise HTTPException(status_code=404, detail="Optimization key not found in table")

        op_id, full_json_str = result
        # If full_json is stored as a JSON string, parse it
        try:
            full_json = json.loads(full_json_str)
        except (TypeError, json.JSONDecodeError):
            full_json = full_json_str  # If it's already a dict or parsing fails, keep as is

        details = get_optimization_details(op_id, conn)
        if not details:
            # No combinations found
            return {
                "completed_combinations": [],
                "pending_combinations": {
                    "pending_count": 0,
                    "sequence_start": None
                },
                "full_json": full_json
            }

        completed_combinations = []
        pending_count = 0
        sequence_start = None

        for detail in details:
            seq_id, status, combination_parameter, response_result = detail
            # Parse response_result if it's a JSON string
            try:
                response = json.loads(response_result) if response_result else None
            except (TypeError, json.JSONDecodeError):
                response = response_result  # Keep as is if parsing fails

            if status.lower() == "success":
                completed_combinations.append(response)
            else:
                pending_count += 1
                if sequence_start is None:
                    sequence_start = seq_id  # Set sequence_start to the first pending sequence_id

        return {
            "completed_combinations": completed_combinations,  # List of response_result
            "pending_combinations": {
                "pending_count": pending_count,
                "sequence_start": sequence_start
            },
            "full_json": full_json
        }

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
