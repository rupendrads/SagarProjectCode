from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
import requests
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
import json
import pandas as pd
# URL for strategy execution
strategy_url = "http://127.0.0.1:8000/run_strategies/"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Models for strategy execution
class Leg(BaseModel):
    atm_straddle_premium: Any
    closest_premium: Any
    expiry: Any
    id: Any
    leg_no: Any
    lots: Any
    no_of_reentry: Any
    option_type: Any
    percent_of_atm_strike_sign: Any
    percent_of_atm_strike_value: Any
    position: Any
    range_breakout: Any
    roll_strike: Any
    roll_strike_increase_in_profit: Any
    roll_strike_lock_profit: Any
    roll_strike_lock_profit_sign: Any
    roll_strike_profit_reaches: Any
    roll_strike_stop_loss: Any
    roll_strike_stop_loss_sign: Any
    roll_strike_strike_type: Any
    roll_strike_trail_profit: Any
    roll_strike_trail_profit_sign: Any
    roll_strike_trailing_options: Any
    simple_momentum: Any
    simple_momentum_direction: Any
    simple_momentum_range_breakout: Any
    simple_momentum_sign: Any
    straddle_width_sign: Any
    straddle_width_value: Any
    strategy_id: Any
    strike_selection_criteria: Any
    strike_selection_criteria_increase_in_profit: Any
    strike_selection_criteria_lock_profit: Any
    strike_selection_criteria_lock_profit_sign: Any
    strike_selection_criteria_profit_reaches: Any
    strike_selection_criteria_stop_loss: Any
    strike_selection_criteria_stop_loss_sign: Any
    strike_selection_criteria_trail_profit: Any
    strike_selection_criteria_trail_profit_sign: Any
    strike_selection_criteria_trailing_options: Any
    strike_type: Any

class OverallStrategy(BaseModel):
    id: Any
    name: Any
    underlying: Any
    strategy_type: Any
    implied_futures_expiry: Any
    entry_time: Any
    last_entry_time: Any
    exit_time: Any
    square_off: Any
    overall_sl: Any
    overall_target: Any
    trailing_options: Any
    profit_reaches: Any
    lock_profit: Any
    increase_in_profit: Any
    trail_profit: Any
    legs: List[Leg]
    fromdate: Any
    todate: Any
    index: Any
    optimization_flag: Optional[bool] = False

@app.post("/run_strategies/")
async def receive_strategy(overall_strategy: OverallStrategy):
    # print(overall_strategy)
    try:
        print(f"optimization_flag is {overall_strategy.optimization_flag}")
        # Prepare payload
        payload = [{
            "strategy_details": {
                "name": overall_strategy.name,
                "index": "NIFTY 50" if overall_strategy.index.lower() == 'nifty' else "NIFTY BANK" if overall_strategy.index.lower() == 'banknifty' else "NIFTY FIN SERVICE",
                "underlying": 'spot' if overall_strategy.underlying == 'spot' else 'implied_futures' if overall_strategy.underlying == 'impliedfutures' else 'futures',
                "strategy_type": overall_strategy.strategy_type,
                "start_date": overall_strategy.fromdate,
                "end_date": overall_strategy.todate,
                "entry_time": f"{overall_strategy.entry_time}:00",
                "last_entry_time" : f"{overall_strategy.last_entry_time}:00" if overall_strategy.last_entry_time is not False else f"{overall_strategy.exit_time}:00",
                "exit_time": f"{overall_strategy.exit_time}:00",
                "square_off": overall_strategy.square_off,
                "overall_sl": overall_strategy.overall_sl if overall_strategy.overall_sl != 0 else False,
                "overall_target": overall_strategy.overall_target if overall_strategy.overall_target != 0 else False,
                "trailing_for_strategy": False if overall_strategy.profit_reaches == 0 else {
                    "trail_type": overall_strategy.trailing_options, 
                    "priceMove": overall_strategy.profit_reaches, 
                    "sl_adjustment": overall_strategy.lock_profit
                } if overall_strategy.trailing_options == "lock" else {
                    "trail_type": "lock_and_trail", 
                    "lock_adjustment": {
                        "priceMove": overall_strategy.profit_reaches, 
                        "sl_adjustment": overall_strategy.lock_profit, 
                        "trail_priceMove": overall_strategy.increase_in_profit, 
                        "trail_sl_adjustment": overall_strategy.trail_profit
                    }
                },
                "implied_futures_expiry": overall_strategy.implied_futures_expiry,
                "optimization_flag": overall_strategy.optimization_flag
            }
        }]
        # print(payload)
        list_of_legs = []
        for leg in overall_strategy.legs:
            try:
                # print(leg)
                leg_detail = {
                    "leg_name": leg.id,
                    "total_lots": leg.lots,
                    "position": leg.position,
                    "option_type": "CE" if leg.option_type == "call" else "PE",
                    "expiry": leg.expiry.lower(),
                    "strike_selection_criteria":  {"strike_selection" : leg.strike_selection_criteria, "value": leg.strike_type} if leg.strike_selection_criteria == "strike" \
                                                    else {"strike_selection" : "closest_premium", "value": leg.closest_premium} if leg.strike_selection_criteria =="closestpremium" \
                                                    else {"strike_selection" : "straddle_width",  "value": {"atm_strike" : leg.straddle_width_sign, "input": leg.straddle_width_value}} if leg.strike_selection_criteria =="straddlewidth"\
                                                    else {"strike_selection" : "atm_pct", "value": {"atm_strike": leg.percent_of_atm_strike_sign, "input": leg.percent_of_atm_strike_value}} if leg.strike_selection_criteria == "percentofatmstrike" \
                                                    else {"strike_selection": "atm_straddle_premium", "value" : leg.atm_straddle_premium },
                                                    
                    "roll_strike": False if leg.roll_strike == 0 else {
                        'roll_strike': leg.roll_strike,
                        'roll_strike_strike_type' : leg.roll_strike_strike_type,
                        'roll_stop_loss': [leg.roll_strike_stop_loss, leg.roll_strike_stop_loss_sign] if leg.roll_strike_stop_loss != 0 else False,
                        'roll_trailing_sl' : (
                            False if leg.roll_strike_profit_reaches == 0 
                            else {
                                "trail_value_type": leg.roll_strike_lock_profit_sign, 
                                "trail_type": "lock", 
                                "priceMove": leg.roll_strike_profit_reaches, 
                                "sl_adjustment": leg.roll_strike_lock_profit
                            } if leg.roll_strike_trailing_options == "lock" 
                            else {
                                "trail_value_type": leg.roll_strike_lock_profit_sign, 
                                "trail_type": "lock_and_trail", 
                                "lock_adjustment": {
                                    "priceMove": leg.roll_strike_profit_reaches, 
                                    "sl_adjustment": leg.roll_strike_lock_profit,
                                    "trail_priceMove": leg.roll_strike_increase_in_profit, 
                                    "trail_sl_adjustment": leg.roll_strike_trail_profit
                                }, 
                                
                            } if leg.roll_strike_trailing_options == "lockntrail"
                            else False)  #                       
                        },

                    "stop_loss": ['points', 10000] if leg.strike_selection_criteria_stop_loss == 0 else [leg.strike_selection_criteria_stop_loss_sign, leg.strike_selection_criteria_stop_loss],
                "trailing_sl": (
                    {"trail_value_type": leg.strike_selection_criteria_lock_profit_sign, 
                    "trail_type": "lock", 
                    "priceMove": leg.strike_selection_criteria_profit_reaches, 
                    "sl_adjustment": leg.strike_selection_criteria_lock_profit
                    } 
                    if leg.strike_selection_criteria_trailing_options == "lock" 
                    else 
                    {"trail_value_type": leg.strike_selection_criteria_lock_profit_sign, 
                    "trail_type": "lock_and_trail", 
                    "lock_adjustment": {
                        "priceMove": leg.strike_selection_criteria_profit_reaches, 
                        "sl_adjustment": leg.strike_selection_criteria_lock_profit, 
                        "trail_priceMove": leg.strike_selection_criteria_increase_in_profit, 
                        "trail_sl_adjustment": leg.strike_selection_criteria_trail_profit
                    }
                    } 
                    if leg.strike_selection_criteria_trailing_options == "lockntrail" 
                    else False
                ),
                    "no_of_reentry": leg.no_of_reentry,
                    "simple_momentum" : False if leg.simple_momentum_range_breakout != "sm" else {"value_type":"points" if leg.simple_momentum_sign =="points" else "percentage", "direction": "increment" if leg.simple_momentum_direction =='+' else "decay", "value": leg.simple_momentum},
                    "range_breakout" : False
                }
            except Exception as e:
                print(e)
            list_of_legs.append(leg_detail)
        print(f"list of legs is {list_of_legs}")
            # print(leg_detail)
        # print(list_of_legs)
        payload[0]["legs"] = list_of_legs
        
        
        # Send request to strategy execution URL
        response = requests.post(strategy_url, json=payload)
        return response.json()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Models for the trading days validator
class MissingDatesResponse(BaseModel):
    status: bool
    missing_dates: List[str] = []
    error: Optional[str] = None
    date_range: Optional[str] = None


# Database-related functions
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


def extract_date_from_filename(filename: str) -> datetime.date:
    date_str = filename.split('_')[-1].replace('.csv', '')
    return datetime.strptime(date_str, '%d%m%Y').date()


def get_dates_from_table(conn: mysql.connector.connection.MySQLConnection) -> List[datetime.date]:
    try:
        cursor = conn.cursor()
        query = """
        SELECT DISTINCT file_name 
        FROM upload_status
        WHERE status = 1 AND file_name LIKE '%.csv'
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"No data found in table upload_status")
        
        dates = [extract_date_from_filename(row[0]) for row in rows]
        return sorted(dates)
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data from upload_status: {e}")


def find_missing_days(conn: mysql.connector.connection.MySQLConnection, upload_dates: List[datetime.date]) -> List[datetime.date]:
    try:
        cursor = conn.cursor()
        
        if upload_dates:
            start_date = min(upload_dates)
            end_date = max(upload_dates)
        
            query = f"""
            SELECT trading_day
            FROM trading_days
            WHERE trading_day >= '{start_date}' AND trading_day <= '{end_date}'
            """
            cursor.execute(query)
            trading_days = {row[0] for row in cursor.fetchall()}
            
            if not trading_days:
                raise HTTPException(status_code=404, detail=f"No data found in table trading_days")
            
            return sorted(set(trading_days) - set(upload_dates))
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data from trading_days: {e}")


def erase_missing_dates_file() -> None:
    try:
        if os.path.exists("missing_dates_files.txt"):
            os.remove("missing_dates_files.txt")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete missing_dates_files.txt: {e}")


def save_missing_dates_files(missing_days: List[datetime.date]) -> None:
    try:
        with open("missing_days.txt", "w") as f:
            for day in missing_days:
                file_name = f"GFDLNFO_BACKADJUSTED_{day.strftime('%d%m%Y')}.csv"
                f.write(f"{file_name}\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save missing_days.txt: {e}")


# Endpoint for the trading days validator
@app.get("/tradingdaysvalidator", response_model=MissingDatesResponse)
async def tradingdaysvalidator(
    db_host: str = Query(..., alias="db_host"),
    db_user: str = Query(..., alias="db_user"),
    db_password: str = Query(..., alias="db_password"),
    db_name: str = Query(..., alias="db_name")
) -> MissingDatesResponse:
    conn = None
    try:
        conn = connect_to_db(db_host, db_user, db_password, db_name)
        
        dates = get_dates_from_table(conn)
        if dates:
            missing_days = find_missing_days(conn, dates)
            if missing_days:
                save_missing_dates_files(missing_days)
            date_range = f"{min(dates)} to {max(dates)}"
            return MissingDatesResponse(
                status=True,
                missing_dates=[str(day) for day in missing_days] if missing_days else [],
                date_range=date_range
            )
        else:
            return MissingDatesResponse(status=True, missing_dates=[], date_range=None)

    except HTTPException as e:
        erase_missing_dates_file()
        return MissingDatesResponse(status=False, error=str(e.detail))
    
    except Exception as e:
        erase_missing_dates_file()
        return MissingDatesResponse(status=False, error=f"An unexpected error occurred: {e}")
    
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Database connection closed.")

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

def get_files_from_db(conn: mysql.connector.connection.MySQLConnection) -> List[str]:
    try:
        cursor = conn.cursor()
        query = "SELECT file_name FROM upload_status WHERE status = 1"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No files found in the database")
        
        return [row[0] for row in rows]
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
    finally:
        if cursor:
            cursor.close()

def check_upload_count(file_name: str, conn: mysql.connector.connection.MySQLConnection):
    if conn:
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
            cursor.fetchall()  
            return result[0] if result else None
        except mysql.connector.errors.InternalError as e:
            print(f"Error fetching upload count: {e}")
        finally:
            if cursor:
                cursor.close()
    return None


class ValidateDbDataResponse(BaseModel):
    status: bool
    message: Optional[str] = None
    file_results: List[dict] = []

class FolderPathRequest(BaseModel):
    folderPath: str

@app.get("/validatedbdata", response_model=ValidateDbDataResponse)
async def validatedbdata(
    folder_request: FolderPathRequest,
    db_host: str = Query(..., alias="db_host"),
    db_user: str = Query(..., alias="db_user"),
    db_password: str = Query(..., alias="db_password"),
    db_name: str = Query(..., alias="db_name")
) -> ValidateDbDataResponse:
    conn = connect_to_db(db_host, db_user, db_password, db_name)
    folder_path = folder_request.folderPath

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return ValidateDbDataResponse(status=False, message=f"Folder not found or is not a directory: {folder_path}")

    folder_files = set([filename for filename in os.listdir(folder_path) if filename.endswith('.csv')])
    db_files = set(get_files_from_db(conn))
    
    file_results = []
    discrepancies_found = False

    for filename in folder_files:
        file_path = os.path.join(folder_path, filename)
        
        data = pd.read_csv(file_path)
        csv_count = data.shape[0]
        
        uploaded_data = check_upload_count(filename, conn)
        
        if uploaded_data is None:
            file_status = False
            file_message = 'File is not uploaded in DB'
            discrepancies_found = True
        elif csv_count != uploaded_data:
            file_status = False
            file_message = 'Discrepancy between File and Database records'
            discrepancies_found = True
        else:
            file_status = True
            file_message = 'Database records match File records'
        
        if not file_status: 
            file_results.append({
                'filename': filename,
                'status': file_status,
                'message': file_message,
                'csv_count': csv_count,
                'db_count': uploaded_data
            })

    missing_files = db_files - folder_files
    with open('missing_dates.txt', 'w') as file:
        for x in sorted(missing_files):
            file.write(f"{x}\n")
    for missing_file in missing_files:
        file_results.append({
            'filename': missing_file,
            'status': False,
            'message': 'File is uploaded in DB but missing from folder',
            'csv_count': None,
            'db_count': check_upload_count(missing_file, conn)
        })
        discrepancies_found = True
    json_file = 'file_results.json'
    with open(json_file, 'w') as json_out:
        json.dump(file_results, json_out, indent=4)
    if not file_results:  
        return ValidateDbDataResponse(
            status=True,
            message="All files in the folder are matched with the database"
        )

    return ValidateDbDataResponse(
        status=False,
        message="Discrepancies found in the folder processing",
        file_results=file_results
    )


# Main for running the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
