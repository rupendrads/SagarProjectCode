import itertools
import json
import requests  
import mysql.connector
from datetime import datetime, timedelta
from typing import Any, Dict, List, Union, Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from constants import db_credentials  
from mysql.connector import Error
from relation import validate_relations
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sagar_common_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'Sagar_common'))
print(f"Sagar_common path: {sagar_common_path}")
if os.path.isdir(sagar_common_path):
    sys.path.append(sagar_common_path)
else:
    print(f"Directory {sagar_common_path} does not exist!")

try:
    from common_function import fetch_parameter
except ImportError as e:
    print(f"Error importing 'fetch_parameter': {e}")
environment = "dev"


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
class KeyRequest(BaseModel):
    optimization_key: str

class LegModel(BaseModel):
    atm_straddle_premium: Union[int, dict, str, bool]
    closest_premium: Union[int, dict, str, bool]
    expiry: Union[int, dict, str, bool]
    id: Union[int, dict, str, bool]
    leg_no: Union[int, dict, str, bool]
    lots: Union[int, dict, str, bool] 
    no_of_reentry: Union[int, dict, str, bool]
    option_type: Union[int, dict, str, bool]
    percent_of_atm_strike_sign: Union[int, dict, str, bool]
    percent_of_atm_strike_value: Union[int, dict, str, bool]
    position: Union[int, dict, str, bool]
    range_breakout: Union[int, dict, str, bool]
    roll_strike: Union[int, dict, str, bool]
    roll_strike_increase_in_profit: Union[int, dict, str, bool]
    roll_strike_lock_profit: Union[int, dict, str, bool]
    roll_strike_lock_profit_sign: Union[int, dict, str, bool]
    roll_strike_profit_reaches: Union[int, dict, str, bool]
    roll_strike_stop_loss: Union[int, dict, str, bool]
    roll_strike_stop_loss_sign: Union[int, dict, str, bool]
    roll_strike_strike_type: Union[int, dict, str, bool]
    roll_strike_trail_profit: Union[int, dict, str, bool]
    roll_strike_trail_profit_sign: Union[int, dict, str, bool]
    roll_strike_trailing_options: Union[int, dict, str, bool]
    simple_momentum: Union[int, dict, str, bool]
    simple_momentum_direction: Union[int, dict, str, bool]
    simple_momentum_range_breakout: Union[int, dict, str, bool]
    simple_momentum_sign: Union[int, dict, str, bool]
    straddle_width_sign: Union[int, dict, str, bool]
    straddle_width_value: Union[int, dict, str, bool]
    strategy_id: Union[int, dict, str, bool]
    strike_selection_criteria: Union[int, dict, str, bool]
    strike_selection_criteria_increase_in_profit: Union[int, dict, str, bool]
    strike_selection_criteria_lock_profit: Union[int, dict, str, bool]
    strike_selection_criteria_lock_profit_sign: Union[int, dict, str, bool]
    strike_selection_criteria_profit_reaches: Union[int, dict, str, bool]
    strike_selection_criteria_stop_loss: Union[int, dict, str, bool]
    strike_selection_criteria_stop_loss_sign: Union[int, dict, str, bool]
    strike_selection_criteria_trail_profit: Union[int, dict, str, bool]
    strike_selection_criteria_trail_profit_sign: Union[int, dict, str, bool]
    strike_selection_criteria_trailing_options: Union[int, dict, str, bool]
    strike_type: Union[int, dict, str, bool]

class DetailRequest(BaseModel):
    optimization_key: str
    sequence_id: int

class OptimizationParameterModel(BaseModel):
    entry_time: Union[int, dict, str, bool]
    exit_time: Union[int, dict, str, bool]
    last_entry_time: Union[int, dict, str, bool]
    fromdate: Union[int, dict, str, bool]
    id: Union[int, dict, str, bool]
    implied_futures_expiry: Union[int, dict, str, bool]
    increase_in_profit: Union[int, dict, str, bool]
    index: Union[int, dict, str, bool]
    lock_profit: Union[int, dict, str, bool]
    name: Union[int, dict, str, bool]
    overall_sl: Union[int, dict, str, bool]
    overall_target: Union[int, dict, str, bool]
    profit_reaches: Union[int, dict, str, bool]
    square_off: Union[int, dict, str, bool]
    strategy_type: Union[int, dict, str, bool]
    todate: Union[int, dict, str, bool]
    trail_profit: Union[int, dict, str, bool]
    trailing_options: Union[int, dict, str, bool]
    underlying: Union[int, dict, str, bool]
    legs: List[Dict[str, Any]]

class DataModel(BaseModel):
    optimization_key: str
    optimization_parameter: OptimizationParameterModel
    strategy_parameter: Dict[str, Any]
def generate_time_intervals(min_time, max_time, interval):
    interval = int(interval)
    min_time = datetime.strptime(min_time, "%H:%M")
    max_time = datetime.strptime(max_time, "%H:%M")
    delta = timedelta(minutes=interval)
    
    times = []
    current_time = min_time
    while current_time <= max_time:
        times.append(current_time.strftime("%H:%M"))
        current_time += delta
    return times

def convert_strike_value(strike):
    if isinstance(strike, int):
        if strike < 0:
            result = f"OTM{abs(strike)}"
        elif strike == 0:
            result = "ATM"
        else:
            result = f"ITM{strike}"
        return result
    return strike

def generate_combinations(param_json):
    param_values = {}
    try:
        for param, config in param_json.items():
            if param == "legs":
                continue  
            if isinstance(config, dict):
                if 'min' in config and 'max' in config and 'interval' in config:
                    if(config["min"]==""):
                        print(f"min is false")
                        
                    print(type(config["min"]), param, config)
                    if isinstance(config["min"], str):
                        param_values[param] = generate_time_intervals(config["min"], config["max"], config["interval"])
                    else:
                        # print(f"{param_values[param]} is the value of {param}")
                        param_values[param] = list(range(config["min"], config["max"] + 1, config["interval"]))
                        print(param)
                else:
                    print(f"getting triggered for {param} and {config}")

                    param_values[param] = [config.get("value", config)]
            elif isinstance(config, bool):
                param_values[param] = [config]
            elif isinstance(config, (str, int)):
                param_values[param] = [config]
            # print(param, config)

        keys, values = zip(*param_values.items())
        all_combinations = [dict(zip(keys, combination)) for combination in itertools.product(*values)]

        if "legs" in param_json:
            legs_combinations = []
            for leg in param_json["legs"]:
                
                leg_param_values = {}
                for param, config in leg.items():
                    
                    
                    if isinstance(config, dict):
                        if "min" in config and "max" in config and "interval" in config:
                            
                            if param in ["strike_selection_criteria_increase_in_profit","strike_selection_criteria_trail_profit",
                                         "roll_strike","atm_straddle_premium", "closest_premium","roll_strike_strike_type",
                                          "roll_strike_stop_loss", "straddle_width_value","roll_strike_profit_reaches", 
                                          "roll_strike_lock_profit","roll_strike_increase_in_profit",
                                          "roll_strike_trail_profit","simple_momentum", "range_breakout",
                                          "percent_of_atm_strike_value"] and config["interval"] == "":
                                leg_param_values[param] = [config.get("min", 0)]
                                print(param, leg_param_values[param])

                            elif isinstance(config["min"], str):
                                leg_param_values[param] = generate_time_intervals(config["min"], config["max"], config["interval"])
                            else:
                                leg_param_values[param] = list(range(config["min"], config["max"] + 1, config["interval"]))
                        else:
                            leg_param_values[param] = [config.get("value", config)]
                    elif isinstance(config, bool):
                        leg_param_values[param] = [config]
                    elif isinstance(config, (str, int)):
                        leg_param_values[param] = [config]

                leg_keys, leg_values = zip(*leg_param_values.items())
                legs_combinations.append([dict(zip(leg_keys, leg_combination)) for leg_combination in itertools.product(*leg_values)])
            combined_with_legs = []
            for comb in all_combinations:
                for leg_comb in itertools.product(*legs_combinations):
                    comb_copy = comb.copy()
                    comb_copy["legs"] = list(leg_comb)
                    combined_with_legs.append(comb_copy)
            all_combinations = combined_with_legs
            all_combinations = all_combinations[:100]
        valid_combinations = [comb for comb in all_combinations if validate_relations(comb)]
        print(f"length of valid combinations is {len(valid_combinations)}")
        for combination in valid_combinations:
            if "legs" in combination and isinstance(combination["legs"], list):
                for leg in combination["legs"]:
                    if (leg.get("strike_selection_criteria") == 'strike') and isinstance(leg.get("strike_type"), int):
                        leg["strike_type"] = convert_strike_value(leg["strike_type"])

        with open("combinations.txt", "w") as file:
            for combination in valid_combinations:
                json_data = json.dumps(combination, indent=4)
                file.write(f"{json_data}\n")
        return len(valid_combinations), valid_combinations
    except Exception as e:
        print(f"error occured in generate_combinations {e}, {param} {config}")



def convert_to_number(data):
    """
    Recursively convert all integer-like or float-like strings to int or float in a nested dictionary or list.
    """
    if isinstance(data, dict):
        return {key: convert_to_number(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_number(item) for item in data]
    else:
        # Check if the data is a string and represents an integer or float (positive or negative)
        try:
            if isinstance(data, str):
                if data.lstrip("-").isdigit():  # Check for integer
                    return int(data)
                elif data.replace("-", "", 1).replace(".", "", 1).isdigit() and data.count(".") == 1:  # Check for float
                    return float(data)
            return data
        except ValueError:
            return data



def save_to_database(data):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='sagar_strategy',
            user='root',
            password='pegasus'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            strategy_id = data['strategy_parameter'].get('id')
            optimization_key = data['optimization_key']
            full_json = json.dumps(data, sort_keys=True)
            check_query = """
                SELECT op_id FROM optimisation
                WHERE strategy_id = %s AND optimization_key = %s
            """
            cursor.execute(check_query, (strategy_id, optimization_key))
            result = cursor.fetchone()

            if result is None:
                insert_query = """
                    INSERT INTO optimisation (strategy_id, optimization_key, full_json)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (strategy_id, optimization_key, full_json))
                connection.commit()
                op_id = cursor.lastrowid
                print(f"Record inserted successfully with op_id: {op_id}.")
            else:
                op_id = result[0]
                print(f"Record already exists with op_id: {op_id}. Skipping insertion.")

            return op_id  

    except mysql.connector.Error as error:
        print(f"Failed to insert data into MySQL table: {error}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
@app.post("/generateKey")
async def process_data(raw_data: Request):
    raw_data = await raw_data.json()
    raw_data = convert_to_number(raw_data)
    file_path = "strategy_parameters.json"

        # Save the parsed JSON data to a file
    with open(file_path, "w") as json_file:
        json.dump(raw_data, json_file, indent=4)
    keys_to_extract = [
    "id", "name", "underlying", "strategy_type", "implied_futures_expiry",
    "square_off", "trailing_options"
    ]
    data = {}
    data["optimization_parameter"] = {}
    data["optimization_parameter"] = {}
    data["strategy_parameter"] = raw_data["strategy_parameter"]
    data["optimization_key"] = raw_data["optimization_key"]
    
    data["optimization_parameter"]["id"] = raw_data["optimization_parameter"]["overallStrategy"]["id"]
    data["optimization_parameter"]["square_off"] = raw_data["optimization_parameter"]["overallStrategy"]["square_off"]
    data["optimization_parameter"]["overall_sl"] = raw_data["optimization_parameter"]["overallStrategy"]["overall_sl"]
    data["optimization_parameter"]["fromdate"] = raw_data["optimization_parameter"]["fromdate"]
    data["optimization_parameter"]["todate"] = raw_data["optimization_parameter"]["todate"]
    data["optimization_parameter"]["index"] = raw_data["optimization_parameter"]["index"]
    data["optimization_parameter"]["overall_target"] = raw_data["optimization_parameter"]["overallStrategy"]["overall_target"]
    data["optimization_parameter"]["trailing_options"] = raw_data["optimization_parameter"]["overallStrategy"]["trailing_options"]
    data["optimization_parameter"]["profit_reaches"] = raw_data["optimization_parameter"]["overallStrategy"]["profit_reaches"]
    data["optimization_parameter"]["lock_profit"] = raw_data["optimization_parameter"]["overallStrategy"]["lock_profit"]
    data["optimization_parameter"]["increase_in_profit"] = raw_data["optimization_parameter"]["overallStrategy"]["increase_in_profit"]
    data["optimization_parameter"]["trail_profit"] = raw_data["optimization_parameter"]["overallStrategy"]["trail_profit"]
    data["optimization_parameter"]["entry_time"] = raw_data["optimization_parameter"]["overallStrategy"]["entry_time"]
    data["optimization_parameter"]["exit_time"] = raw_data["optimization_parameter"]["overallStrategy"]["exit_time"]
    data["optimization_parameter"]["last_entry_time"] = raw_data["optimization_parameter"]["overallStrategy"]["last_entry_time"]
    data["optimization_parameter"]["name"] = raw_data["optimization_parameter"]["overallStrategy"]["name"]
    data["optimization_parameter"]["underlying"] = raw_data["optimization_parameter"]["overallStrategy"]["underlying"]
    data["optimization_parameter"]["strategy_type"] = raw_data["optimization_parameter"]["overallStrategy"]["strategy_type"]
    data["optimization_parameter"]["implied_futures_expiry"] = raw_data["optimization_parameter"]["overallStrategy"]["implied_futures_expiry"]
    
    data["optimization_parameter"]["legs"] = raw_data["optimization_parameter"]["legs"]
    if data["optimization_parameter"]["trailing_options"]=="lock":
        if data["optimization_parameter"]["profit_reaches"]["min"]=="":
            data["optimization_parameter"]["lock_profit"] = data["strategy_parameter"]["lock_profit"]
            data["optimization_parameter"]["profit_reaches"] = data["strategy_parameter"]["profit_reaches"]
        data["optimization_parameter"]["increase_in_profit"] = 0
        data["optimization_parameter"]["trail_profit"] = 0 

    if data["optimization_parameter"]["trailing_options"]=="lockntrail":
        if data["optimization_parameter"]["profit_reaches"]["min"]=="":
            data["optimization_parameter"]["lock_profit"] = data["strategy_parameter"]["lock_profit"]
            data["optimization_parameter"]["profit_reaches"] = data["strategy_parameter"]["profit_reaches"]
            data["optimization_parameter"]["increase_in_profit"] = data["strategy_parameter"]["increase_in_profit"]
            data["optimization_parameter"]["trail_profit"] = data["strategy_parameter"]["trail_profit"]
 
    
    try:
        # print(data)
        param_json = data["optimization_parameter"]#.dict()
        # print(param_json)
        valid_combinations_length, valid_combinations = generate_combinations(param_json)
        # print(valid_combinations_length, valid_combinations)
        op_id = save_to_database(raw_data)
        print(f"op_id received is {op_id}")
        if op_id is None:
            raise HTTPException(status_code=500, detail="Failed to save optimization data.")
        connection = mysql.connector.connect(
            host='localhost',
            database='sagar_strategy',
            user='root',
            password='pegasus'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Prepare insert query for optimisation_details
            insert_details_query = """
                INSERT INTO optimisation_details (op_id, combination_parameter, status, response_result, timestamp, user, sequence_id)
                VALUES (%s, %s, %s, %s, NOW(), %s, %s)
            """
            
            # Prepare data for batch insert
            insert_values = []
            sequence_id = 1
            for combination in valid_combinations:
                combination_parameter = json.dumps(combination)
                status = 'pending'
                response_result = None
                user = 'admin'
                insert_values.append((op_id, combination_parameter, status, response_result, user, sequence_id))
                sequence_id += 1
            chunk_size = 10000
            total_records = len(insert_values)
            for i in range(0, total_records, chunk_size):
                chunk = insert_values[i:i + chunk_size]
                cursor.executemany(insert_details_query, chunk)
                connection.commit()
            print("inserted all combinations into optimisation_details")
            # cursor.executemany(insert_details_query, insert_values)

            connection.commit()
            print(f"Inserted {valid_combinations_length} combinations into optimisation_details.")

        return {"total_number_of_combinations": valid_combinations_length}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()








def connect_to_db() -> mysql.connector.connection.MySQLConnection:
    try:
        conn = mysql.connector.connect(
            host=db_credentials['host'],
            database=db_credentials['database'],
            user=db_credentials['user'],
            password=db_credentials['password']
        )
        if conn.is_connected():
            print("Connected to the database.")
            return conn
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")



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

def get_combination_parameter(op_id: int, sequence_id: int, conn: mysql.connector.connection.MySQLConnection):
    try:
        cursor = conn.cursor(buffered=True)
        query = """
            SELECT combination_parameter FROM optimisation_details
            WHERE op_id = %s AND sequence_id = %s
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

def update_response_result(op_id: int, sequence_id: int, response_result: dict, conn: mysql.connector.connection.MySQLConnection):
    try:
        cursor = conn.cursor()
        query = """
            UPDATE optimisation_details
            SET response_result = %s, status = %s
            WHERE op_id = %s AND sequence_id = %s
        """
        response_result_json = json.dumps(response_result)
        status = 'success'  
        cursor.execute(query, (response_result_json, status, op_id, sequence_id))
        conn.commit()
        print(f"Updated response_result and status for op_id: {op_id}, sequence_id: {sequence_id}")
    except mysql.connector.Error as e:
        print(f"Error updating response_result and status: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating response_result and status: {e}")
    finally:
        if cursor:
            cursor.close()

def get_tradebook(op_id: int,sequence_id:int,conn: mysql.connector.connection.MySQLConnection):
    try:
        cursor = conn.cursor(buffered=True)
        query = """
            SELECT response_result FROM optimisation_details
            WHERE op_id = %s AND sequence_id= %s
        """
        cursor.execute(query, (op_id,sequence_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as e:
        print(f"Error fetching op_id: {e}")
        return None
    finally:
        if cursor:
            cursor.close()








def connect_to_db() -> mysql.connector.connection.MySQLConnection:
    try:
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
                SELECT sequence_id, status, combination_parameter, response_result 
                FROM optimisation_details
                WHERE op_id = %s
                ORDER BY sequence_id ASC
            """
            cursor.execute(query, (op_id,))
            print(query, op_id)
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
        try:
            full_json = json.loads(full_json_str)
        except (TypeError, json.JSONDecodeError):
            full_json = full_json_str  

        details = get_optimization_details(op_id, conn)
        if not details:
            return {
                "completed_combinations": [],
                "pending_combinations": {
                    "pending_count": 0,
                    "sequence_start": None,
                    "total_count": 0
                },
                "full_json": full_json
            }

        completed_combinations = []
        pending_count = 0
        sequence_start = None

        for detail in details:
            seq_id, status, combination_parameter, response_result = detail
            try:
                response = json.loads(response_result) if response_result else None
            except (TypeError, json.JSONDecodeError):
                response = response_result  

            if status.lower() == "success":
                # Include sequence_id with each response
                completed_combinations.append({
                    "sequence_id": seq_id,
                    "response": response
                })
            else:
                pending_count += 1
                if sequence_start is None:
                    sequence_start = seq_id 
        total_count = len(completed_combinations) + pending_count
        
        return {
            "completed_combinations": completed_combinations,  
            "pending_combinations": {
                "total_count": total_count,
                "pending_count": pending_count,
                "sequence_start": sequence_start
            },
            "full_json": full_json
        }

    finally:
        if conn:
            conn.close()
@app.post("/gettradebook", response_model=dict)
async def save_portfolio(data: dict):
    conn = None
    conn = connect_to_db()

    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        optimization_key = data.get("optimization_key")
        sequence_id = data.get("sequence_id")
        print(optimization_key, sequence_id)
        op_id = get_op_id(optimization_key, conn)
        if not op_id:
            raise HTTPException(status_code=404, detail="Optimization key not found in optimisation table")
        
        response_result = get_tradebook(op_id, sequence_id, conn)
        
        if response_result is None:
            raise HTTPException(status_code=404, detail="Tradebook not found")

        # Parse response_result if it's a JSON string
        return json.loads(response_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# @app.post("/retryOptimization")
# async def getallcombinations(key_request: KeyRequest):
#     key_value = key_request.optimization_key
#     print(f"optimization key is {key_value}")
#     conn = None
#     try:
#         conn = connect_to_db()
        
#         result = get_optimization(key_value, conn)
#         if not result:
#             raise HTTPException(status_code=404, detail="Optimization key not found in table")

#         op_id, full_json_str = result
#         try:
#             full_json = json.loads(full_json_str)
#         except (TypeError, json.JSONDecodeError):
#             full_json = full_json_str  

#         details = get_optimization_details(op_id, conn)
#         if not details:
#             return {
#                 "completed_combinations": [],
#                 "pending_combinations": {
#                     "pending_count": 0,
#                     "sequence_start": None,
#                     "total_count": 0
#                 },
#                 "full_json": full_json
#             }

#         completed_combinations = []
#         pending_count = 0
#         sequence_start = None

#         for detail in details:
#             seq_id, status, combination_parameter, response_result = detail
#             try:
#                 response = json.loads(response_result) if response_result else None
#             except (TypeError, json.JSONDecodeError):
#                 response = response_result  

#             if status.lower() == "success":
#                 # response.pop("tradebook", None)
#                 completed_combinations.append({"response" : response})
#             else:
#                 pending_count += 1
#                 if sequence_start is None:
#                     sequence_start = seq_id 
#         total_count = len(completed_combinations) + pending_count
        
#         return {
#             "completed_combinations": completed_combinations,  
#             "pending_combinations": {
#                 "total_count": total_count,
#                 "pending_count": pending_count,
#                 "sequence_start": sequence_start
#             },
#             "full_json": full_json
#         }

#     finally:
#         if conn:
#             conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9001)
