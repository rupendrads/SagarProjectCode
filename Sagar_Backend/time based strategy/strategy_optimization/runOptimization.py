from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import json
import requests  # Import requests to make HTTP requests
#from constants import db_credentials  # Replace with your actual credentials module

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current script
    sagar_common_path = os.path.join(current_dir, "../../../Sagar_common")  # Go up two levels to "OGCODE"
    if sagar_common_path not in sys.path:
        sys.path.append(sagar_common_path)
    from common_function import fetch_parameter
except ImportError as e:
    print(f"Error fetching db details: {e}")
    raise HTTPException(status_code=500, detail="Failed to import common functions.")

app = FastAPI()

# Database connection function
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

# Request model
class DetailRequest(BaseModel):
    optimization_key: str
    sequence_id: int

# Function to get op_id from optimisation table
def get_op_id(optimization_key: str, conn: mysql.connector.connection.MySQLConnection):
    try:
        cursor = conn.cursor(buffered=True)
        query = """
            SELECT op_id FROM optimisation
            WHERE optimization_key = %s
        """
        cursor.execute(query, (optimization_key,))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as e:
        print(f"Error fetching op_id: {e}")
        return None
    finally:
        if cursor:
            cursor.close()

# Function to get combination_parameter from optimisation_details table
def get_combination_parameter(op_id: int, sequence_id: int, conn: mysql.connector.connection.MySQLConnection):
    try:
        cursor = conn.cursor(buffered=True)
        query = """
            SELECT combination_parameter FROM optimisation_details
            WHERE op_id = %s AND id = %s
        """
        cursor.execute(query, (op_id, sequence_id))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as e:
        print(f"Error fetching combination_parameter: {e}")
        return None
    finally:
        if cursor:
            cursor.close()

# Function to update response_result and status in optimisation_details table
def update_response_result(op_id: int, sequence_id: int, response_result: dict, conn: mysql.connector.connection.MySQLConnection):
    try:
        cursor = conn.cursor()
        query = """
            UPDATE optimisation_details
            SET response_result = %s, status = %s
            WHERE op_id = %s AND sequence_id = %s
        """
        response_result_json = json.dumps(response_result)
        status = 'success'  # Update the status to 'Success'
        cursor.execute(query, (response_result_json, status, op_id, sequence_id))
        conn.commit()
        print(f"Updated response_result and status for op_id: {op_id}, sequence_id: {sequence_id}")
    except mysql.connector.Error as e:
        print(f"Error updating response_result and status: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating response_result and status: {e}")
    finally:
        if cursor:
            cursor.close()

@app.post("/runOptimization")
async def get_combination(detail_request: DetailRequest):
    optimization_key = detail_request.optimization_key
    sequence_id = detail_request.sequence_id
    conn = None
    try:
        conn = connect_to_db()
        op_id = get_op_id(optimization_key, conn)
        if not op_id:
            raise HTTPException(status_code=404, detail="Optimization key not found in optimisation table")

        combination_parameter = get_combination_parameter(op_id, sequence_id, conn)
        if not combination_parameter:
            raise HTTPException(status_code=404, detail="Combination not found with given sequence_id and op_id")

        # Attempt to parse combination_parameter as JSON
        try:
            combination = json.loads(combination_parameter)
        except (TypeError, json.JSONDecodeError):
            combination = combination_parameter  # Return as is if parsing fails

        # Add optimization_flag to the combination
        combination["optimization_flag"] = True
        print(combination)
        # Send combination to /run_strategies
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                "http://127.0.0.1:8080/run_strategies",
                headers=headers,
                json=combination  # Send the combination as JSON
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            run_strategies_response = response.json()  # Assuming the response is JSON
        except requests.exceptions.RequestException as e:
            print(f"Error sending request to /run_strategies: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with /run_strategies: {e}")

        # If the response is fine, update the optimisation_details table
        run_strategies_response['parameters'] = combination
        update_response_result(op_id, sequence_id, run_strategies_response, conn)

        # Return the response from /run_strategies
        return run_strategies_response
    finally:
        if conn:
            conn.close()

# Run the application on a different port (e.g., 8090)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)
