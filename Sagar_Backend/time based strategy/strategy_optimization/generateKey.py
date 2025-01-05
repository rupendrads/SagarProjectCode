# fastapi_app.py

import itertools
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from relation import validate_relations
import json
from typing import Any, Dict, List, Union

# Import MySQL connector
import mysql.connector
from mysql.connector import Error

app = FastAPI()

def generate_time_intervals(min_time, max_time, interval):
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

    for param, config in param_json.items():
        if param == "legs":
            continue  
        if isinstance(config, dict):
            if "min" in config and "max" in config and "interval" in config:
                if isinstance(config["min"], str):
                    param_values[param] = generate_time_intervals(config["min"], config["max"], config["interval"])
                else:
                    param_values[param] = list(range(config["min"], config["max"] + 1, config["interval"]))
            else:
                param_values[param] = [config.get("value", config)]
        elif isinstance(config, bool):
            param_values[param] = [config]
        elif isinstance(config, (str, int)):
            param_values[param] = [config]

    keys, values = zip(*param_values.items())
    all_combinations = [dict(zip(keys, combination)) for combination in itertools.product(*values)]

    if "legs" in param_json:
        legs_combinations = []
        for leg in param_json["legs"]:
            leg_param_values = {}
            for param, config in leg.items():
                if isinstance(config, dict):
                    if "min" in config and "max" in config and "interval" in config:
                        if isinstance(config["min"], str):
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

    valid_combinations = [comb for comb in all_combinations if validate_relations(comb)]

    for combination in valid_combinations:
        if "legs" in combination and isinstance(combination["legs"], list):
            for leg in combination["legs"]:
                if (leg.get("strike_selection_criteria") == 'strike') and isinstance(leg.get("strike_type"), int):
                    leg["strike_type"] = convert_strike_value(leg["strike_type"])

    # Save combinations to a file (optional)
    with open("combinations.txt", "w") as file:
        for combination in valid_combinations:
            json_data = json.dumps(combination, indent=4)
            file.write(f"{json_data}\n")
    return len(valid_combinations), valid_combinations

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



def save_to_database(data):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host='localhost',
            database='sagar_strategy',
            user='root',
            password='pegasus'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Prepare data for insertion
            strategy_id = data.strategy_parameter.get('id')
            optimization_key = data.optimization_key
            # Ensure consistent JSON string representation by sorting keys
            full_json = json.dumps(data.dict(), sort_keys=True)

            # Check if the same record exists
            check_query = """
                SELECT op_id FROM optimisation
                WHERE strategy_id = %s AND optimization_key = %s
            """
            cursor.execute(check_query, (strategy_id, optimization_key))
            result = cursor.fetchone()

            if result is None:
                # If no record exists, insert into the 'optimisation' table
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

            return op_id  # Return the op_id for further use

    except mysql.connector.Error as error:
        print(f"Failed to insert data into MySQL table: {error}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
@app.post("/generateKey")
def process_data(data: DataModel):
    try:
        param_json = data.optimization_parameter.dict()
        valid_combinations_length, valid_combinations = generate_combinations(param_json)

        # Save to optimisation table and get op_id
        op_id = save_to_database(data)
        print(f"op_id received is {op_id}")
        if op_id is None:
            raise HTTPException(status_code=500, detail="Failed to save optimization data.")

        # Connect to the database
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
            cursor.executemany(insert_details_query, insert_values)

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






@app.post("/process")
def process_data(data: DataModel):
    try:
        param_json = data.optimization_parameter.dict()
        valid_combinations_length, valid_combination = generate_combinations(param_json)

        save_to_database(data)
        # print(valid_combination)
        return {"total_number_of_combinations": valid_combinations_length}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
