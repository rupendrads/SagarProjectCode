from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import json
import requests  
from typing import List, Dict, Any, Optional
from Strategy import Strategy
from LegBuilder import LegBuilder
from utils import  convert_dates_to_string, assign_index, read_strategy_folder, process_pnl_files, process_nfo_lot_file, combined_report_generator, analyse_combined_strategy, update_tradebook_with_strategy_pnl,analyze_tradebook, update_tradebook_with_pnl, process_strategy_constraints
import logging
import os
import gzip
import shutil
import math
from datetime import datetime, timedelta
import glob
import pandas as pd
import json
import asyncio
import warnings
from fastapi.middleware.cors import CORSMiddleware
import time
import random
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


from data import get_expiry_df, get_underlying_ltp
db_credentials = fetch_parameter(environment, "db_sagar_strategy" )
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)
# Database connection function
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

#Function to get the tradebook


# Function to get combination_parameter from optimisation_details table
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

# Function to update response_result and status in optimisation_details table
def update_response_result(op_id: int, sequence_id: int, response_result: dict):
    # Connect to the database using credentials from db_credentials
    conn = None
    try:
        conn = mysql.connector.connect(
            host=db_credentials["host"],
            user=db_credentials["user"],
            password=db_credentials["password"],
            database=db_credentials["database"]
        )
        

        cursor = conn.cursor()
        query = """
            UPDATE optimisation_details
            SET response_result = %s, status = %s
            WHERE op_id = %s AND sequence_id = %s
        """
        response_result_json = json.dumps(response_result)
        
        status = 'success'
        
        # Execute the query
        cursor.execute(query, (response_result_json, status, op_id, sequence_id))
        conn.commit()
        print(f"Updated response_result and status for op_id: {op_id}, sequence_id: {sequence_id}")
    except mysql.connector.Error as e:
        print(f"Error updating response_result and status: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating response_result and status: {e}")
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("Database connection closed.")

@app.post("/runOptimization")
async def get_combination(detail_request: DetailRequest):
    print(detail_request)
    optimization_key = detail_request.optimization_key
    sequence_id = detail_request.sequence_id
    print(optimization_key, sequence_id)

    # Connect to the database

    conn = None
    try:
        conn = connect_to_db()
        op_id = get_op_id(optimization_key, conn)
        print(f"op_id is {op_id}")

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
        overall_strategy = combination
        print(overall_strategy)
        payload = [{
            "strategy_details": {
                "name": overall_strategy["name"],
                "index": "NIFTY 50" if overall_strategy["index"].lower() == 'nifty' else "NIFTY BANK" if overall_strategy["index"].lower() == 'banknifty' else "NIFTY FIN SERVICE",
                "underlying": 'spot' if overall_strategy["underlying"] == 'spot' else 'implied_futures' if overall_strategy["underlying"] == 'impliedfutures' else 'futures',
                "strategy_type": overall_strategy["strategy_type"],
                "start_date": overall_strategy["fromdate"],
                "end_date": overall_strategy["todate"],
                "entry_time": f"{overall_strategy['entry_time']}:00",
                "last_entry_time": f"{overall_strategy['last_entry_time']}:00" if overall_strategy["last_entry_time"] is not False else f"{overall_strategy['exit_time']}:00",
                "exit_time": f"{overall_strategy['exit_time']}:00",
                "square_off": overall_strategy["square_off"],
                "overall_sl": overall_strategy["overall_sl"] if overall_strategy["overall_sl"] != 0 else False,
                "overall_target": overall_strategy["overall_target"] if overall_strategy["overall_target"] != 0 else False,
                "trailing_for_strategy": False if overall_strategy["profit_reaches"] == 0 else {
                    "trail_type": overall_strategy["trailing_options"],
                    "priceMove": overall_strategy["profit_reaches"],
                    "sl_adjustment": overall_strategy["lock_profit"]
                } if overall_strategy["trailing_options"] == "lock" else {
                    "trail_type": "lock_and_trail",
                    "lock_adjustment": {
                        "priceMove": overall_strategy["profit_reaches"],
                        "sl_adjustment": overall_strategy["lock_profit"],
                        "trail_priceMove": overall_strategy["increase_in_profit"],
                        "trail_sl_adjustment": overall_strategy["trail_profit"]
                    }
                },
                "implied_futures_expiry": overall_strategy["implied_futures_expiry"],
                "optimization_flag": overall_strategy["optimization_flag"]
            }
        }]

        # print(payload)
        
        list_of_legs = []
        for leg in overall_strategy["legs"]:
            try:
                leg_detail = {
                    "leg_name": leg["id"],
                    "total_lots": leg["lots"],
                    "position": leg["position"],
                    "option_type": "CE" if leg["option_type"] == "call" else "PE",
                    "expiry": leg["expiry"].lower(),
                    "strike_selection_criteria": {
                        "strike_selection": leg["strike_selection_criteria"], 
                        "value": leg["strike_type"]
                    } if leg["strike_selection_criteria"] == "strike" 
                    else {
                        "strike_selection": "closest_premium", 
                        "value": leg["closest_premium"]
                    } if leg["strike_selection_criteria"] == "closestpremium" 
                    else {
                        "strike_selection": "straddle_width",  
                        "value": {"atm_strike": leg["straddle_width_sign"], "input": leg["straddle_width_value"]}
                    } if leg["strike_selection_criteria"] == "straddlewidth" 
                    else {
                        "strike_selection": "atm_pct", 
                        "value": {"atm_strike": leg["percent_of_atm_strike_sign"], "input": leg["percent_of_atm_strike_value"]}
                    } if leg["strike_selection_criteria"] == "percentofatmstrike" 
                    else {
                        "strike_selection": "atm_straddle_premium", 
                        "value": leg["atm_straddle_premium"]
                    },
                    
                    "roll_strike": False if leg["roll_strike"] == 0 else {
                        'roll_strike': leg["roll_strike"],
                        'roll_strike_strike_type': leg["roll_strike_strike_type"],
                        'roll_stop_loss': [leg["roll_strike_stop_loss"], leg["roll_strike_stop_loss_sign"]] if leg["roll_strike_stop_loss"] != 0 else False,
                        'roll_trailing_sl': (
                            False if leg["roll_strike_profit_reaches"] == 0 
                            else {
                                "trail_value_type": leg["roll_strike_lock_profit_sign"], 
                                "trail_type": "lock", 
                                "priceMove": leg["roll_strike_profit_reaches"], 
                                "sl_adjustment": leg["roll_strike_lock_profit"]
                            } if leg["roll_strike_trailing_options"] == "lock" 
                            else {
                                "trail_value_type": leg["roll_strike_lock_profit_sign"], 
                                "trail_type": "lock_and_trail", 
                                "lock_adjustment": {
                                    "priceMove": leg["roll_strike_profit_reaches"], 
                                    "sl_adjustment": leg["roll_strike_lock_profit"],
                                    "trail_priceMove": leg["roll_strike_increase_in_profit"], 
                                    "trail_sl_adjustment": leg["roll_strike_trail_profit"]
                                }
                            } if leg["roll_strike_trailing_options"] == "lockntrail"
                            else False
                        )
                    },

                    "stop_loss": ['points', 10000] if leg["strike_selection_criteria_stop_loss"] == 0 else [leg["strike_selection_criteria_stop_loss_sign"], leg["strike_selection_criteria_stop_loss"]],
                    "trailing_sl": (
                        {
                            "trail_value_type": leg["strike_selection_criteria_lock_profit_sign"], 
                            "trail_type": "lock", 
                            "priceMove": leg["strike_selection_criteria_profit_reaches"], 
                            "sl_adjustment": leg["strike_selection_criteria_lock_profit"]
                        } 
                        if leg["strike_selection_criteria_trailing_options"] == "lock" 
                        else 
                        {
                            "trail_value_type": leg["strike_selection_criteria_lock_profit_sign"], 
                            "trail_type": "lock_and_trail", 
                            "lock_adjustment": {
                                "priceMove": leg["strike_selection_criteria_profit_reaches"], 
                                "sl_adjustment": leg["strike_selection_criteria_lock_profit"], 
                                "trail_priceMove": leg["strike_selection_criteria_increase_in_profit"], 
                                "trail_sl_adjustment": leg["strike_selection_criteria_trail_profit"]
                            }
                        } 
                        if leg["strike_selection_criteria_trailing_options"] == "lockntrail" 
                        else False
                    ),
                    "no_of_reentry": leg["no_of_reentry"],
                    "simple_momentum": False if leg["simple_momentum_range_breakout"] != "sm" else {
                        "value_type": "points" if leg["simple_momentum_sign"] == "points" else "percentage", 
                        "direction": "increment" if leg["simple_momentum_direction"] == '+' else "decay", 
                        "value": leg["simple_momentum"]
                    },
                    "range_breakout": False
                }
            except Exception as e:
                print(e)
            list_of_legs.append(leg_detail)


        payload[0]["legs"] = list_of_legs
        strategy_requests = payload
        strategy_requests[0]['strategy_details']['index'] = assign_index(strategy_requests[0]['strategy_details']['index'])
        implied_futures_expiry = 0 if strategy_requests[0]['strategy_details']['implied_futures_expiry'].lower() == 'current' else 1 if strategy_requests[0]['strategy_details']['implied_futures_expiry'].lower() == 'next' else False
        print(f"--------------{implied_futures_expiry} is implied_futures_expiry------------------------")
        fut_data = get_underlying_ltp(strategy_requests[0]['strategy_details']['index'], strategy_requests[0]['strategy_details']['start_date'], strategy_requests[0]['strategy_details']['end_date'], strategy_requests[0]['strategy_details']['underlying'], strategy_requests[0]['strategy_details']['implied_futures_expiry'])
        print(f"-------------------------futures data---------------------------")
        # print(fut_data.head())
        options_data = get_expiry_df(strategy_requests[0]['strategy_details']['index'], strategy_requests[0]['strategy_details']['start_date'], strategy_requests[0]['strategy_details']['end_date'], "09:15:00", "15:30:00")
           
        results = []

        for strategy_request in strategy_requests:
            strategy_details = strategy_request["strategy_details"]#.dict()
            print(f"--------strategy details----------")
            strategy_details["underlying_data"] = fut_data
            strategy_details["options_data"] = options_data
            # strategy_details["optimization_flag"] = optimization_flag
            strategy = Strategy(**strategy_details)
            
            legs = []
            for leg_detail in strategy_request["legs"]:
                leg = LegBuilder(
                    leg_name=leg_detail["leg_name"],
                    strategy=strategy,
                    total_lots=leg_detail["total_lots"],
                    position=leg_detail["position"],
                    option_type=leg_detail["option_type"],
                    expiry=leg_detail["expiry"],
                    strike_selection_criteria=leg_detail["strike_selection_criteria"],
                    roll_strike=leg_detail["roll_strike"],
                    new_strike_selection_criteria=None,
                    stop_loss=leg_detail["stop_loss"],
                    trailing_sl=leg_detail["trailing_sl"],
                    no_of_reentry=leg_detail["no_of_reentry"],
                    simple_momentum=leg_detail["simple_momentum"],
                    range_breakout=leg_detail["range_breakout"]
                )
                legs.append(leg)
            
            tasks = [leg.backtest_selection() for leg in legs]
            await asyncio.gather(*tasks)
        read_strategy_folder(strategy.name, strategy.square_off)
        process_pnl_files(strategy)
        process_strategy_constraints(strategy)
        analyse_combined_strategy(strategy.name)
        # OverallPerformance = combined_report_generator(strategy)
        OverallPerformance = combined_report_generator(strategy, True)
        tradebook = update_tradebook_with_strategy_pnl(strategy, True)
        tradebook = update_tradebook_with_pnl(tradebook, strategy)    
        os.makedirs(strategy.name, exist_ok=True)
        tradebook.to_csv(os.path.join(strategy.name, f"{strategy.name}_combined_tradebook.csv"), index=False)
        OverallPerformance = analyze_tradebook(strategy)
        result = []
        tradebook['tsl']= tradebook['tsl'].fillna('nan') #testing for no tsl case
        for index, row in tradebook.iterrows():
            result.append({
                "symbol": row['symbol'],
                "trade": row['trade'].upper(),
                "entry_time": row['entry_time'].strftime('%Y-%m-%d %H:%M:%S'),
                "entry_price": row['entry_price'],
                "exit_time": row['exit_time'],
                "exit_price": row['exit_price'],
                "sl": row['sl'],
                "tsl": row['tsl'],
                "qty": row['qty'],
                "pnl": row['pnl'],
                "maxLossStrategy": row['maxLossStrategy'],
                "maxProfitStrategy": row['maxProfitStrategy'],
                # "comment": row['comment']
                "comment": row['comment'] if not (isinstance(row['comment'], float) and math.isnan(row['comment'])) else None
            })
        
        # print(result)
        # print(OverallPerformance)
        if  strategy.optimization_flag:
            print(OverallPerformance)
            print(f"strategy optimizer is {strategy.optimization_flag}")
            newOverallPerformance = OverallPerformance #convert_numpy_types(OverallPerformance)
            response = {
                "netProfit" : (newOverallPerformance["TotalProfit"]),
                "winningTrades": newOverallPerformance["DaysProfit"],
                "losingTrades": newOverallPerformance["DaysLoss"],
                "winningStrike": newOverallPerformance["MaxWinningStreak"],
                "losingStrike": newOverallPerformance["MaxLosingStreak"],
                "expenctancy" : newOverallPerformance["ExpectancyRatio"],
                "averageProfit" : newOverallPerformance["AverageProfit"],
                "averageLoss" : newOverallPerformance["AverageLoss"],
                "maxDrawDown" : newOverallPerformance["MaxDrawdown" ],
                "maxDrawDownDuration" : newOverallPerformance["DurationOfMaxDrawdown"]["days"],
                "systemDrawdown": "0",
                "FundsRequired": 100000,
                "Exposure": 100000,
                "Cagr": 15,
                "parameters": {},#{"strategy_parameters": strategy_details, "legs":legs },
                "numberOfTrades": len(tradebook),
                "totalBrokerage": {}


            }
        overall_performance_df = pd.DataFrame(OverallPerformance)
        overall_performance_df.to_csv(f'{strategy.name}/{strategy.name}_OverallPerformance.csv',index=False)
        print(f"overall perfomance saved")
        response = {
            "OverallPerformance": OverallPerformance,
            "YearlyData": []
        }
        yearly_data = {}
        for _, trade in tradebook.iterrows():
            year = pd.to_datetime(trade['entry_time']).year
            month = pd.to_datetime(trade['entry_time']).strftime('%b')
            pnl = round(trade['pnl'], 2)

            if year not in yearly_data:
                yearly_data[year] = {
                    "Year": year,
                    "MonthlyPerformance": {month: 0 for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']},
                    "Total": 0,
                    "CumulativePnL": [],
                    "Dates": []
                }
            
            yearly_data[year]["MonthlyPerformance"][month] = round(yearly_data[year]["MonthlyPerformance"][month] + pnl, 2)
            yearly_data[year]["Total"] = round(yearly_data[year]["Total"] + pnl, 2)
            yearly_data[year]["CumulativePnL"].append(round(yearly_data[year]["Total"], 2))
            yearly_data[year]["Dates"].append(pd.to_datetime(trade['entry_time']))

        for year, year_data in yearly_data.items():
            print(f"yearwise calculation {year}")
            cumulative_pnl = year_data["CumulativePnL"]
            dates = year_data["Dates"]
            
            max_drawdown = 0
            max_drawdown_duration = timedelta(0)
            max_drawdown_start = None
            max_drawdown_end = None
            peak = cumulative_pnl[0]
            
            for i in range(1, len(cumulative_pnl)):
                if cumulative_pnl[i] > peak:
                    peak = cumulative_pnl[i]
                drawdown = round(peak - cumulative_pnl[i], 2)
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    max_drawdown_end = dates[i]
                    for j in range(i, -1, -1):
                        if cumulative_pnl[j] == peak:
                            max_drawdown_start = dates[j]
                            break
                    max_drawdown_duration = max_drawdown_end - max_drawdown_start

            str_year = str(year)
            year_data["MaxDrawdown"] = OverallPerformance["yearlyDrawdowns"][str_year]['max_drawdown']#round(max_drawdown, 2)
            year_data["DaysForMaxDrawdown"] = OverallPerformance['yearlyDrawdowns'][str_year]["max_drawdown_duration"]#max_drawdown_duration.days
            year_data["DurationOfMaxDrawdown"] = {
                "start": OverallPerformance['yearlyDrawdowns'][str_year]["drawdown_start"].strftime("%d/%m/%Y") if OverallPerformance['yearlyDrawdowns'][str_year]["drawdown_start"] else None,
                "end": OverallPerformance['yearlyDrawdowns'][str_year]["drawdown_end"].strftime("%d/%m/%Y") if OverallPerformance['yearlyDrawdowns'][str_year]["drawdown_start"] else None
            }
            try:
                year_data["ReturnToMaxDDYearly"] = round((year_data["Total"] /  year_data["MaxDrawdown"]) * 100, 2) if year_data["MaxDrawdown"] != 0 else 0
            except:
                year_data["ReturnToMaxDDYearly"] = 0

            del year_data["CumulativePnL"]
            del year_data["Dates"]

            response["YearlyData"].append(year_data)

            response["YearlyData"].sort(key=lambda x: x["Year"])
            # print(f"response result is {response}")
            # print(f"\n \n result is {result}")
            response["tradebook"] = result
            if response:
                response["parameters"] = combination
                response = convert_dates_to_string(response)
                
                
                update_response_result(op_id, sequence_id, response)
                response.pop("tradebook", None)
                server_response = {
                    "status": "success",
                    "sequence_id": sequence_id,
                    "response": response
                }
                
                print(server_response)
                
                return server_response

        
    finally:
        if conn:
            conn.close()




# Run the application on a different port (e.g., 8090)
if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9002)
