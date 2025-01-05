import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
'''
This is a simple validator to check if the trading days are uploaded to the database.
It will return the missing trading days and the date range of the uploaded data.
It will also save the missing trading days to a file called missing_days.txt,
this function can be disabled by disabling the save_missing_days method in line #132
'''
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


class MissingDatesResponse(BaseModel):
    status: bool
    missing_dates: List[str] = []
    error: Optional[str] = None
    date_range: Optional[str] = None


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
            print(f"missing days are {missing_days}")
            if missing_days:
                save_missing_dates_files(missing_days)
            date_range = f"{min(dates)} to {max(dates)}"
            print(f"date range is {date_range}")
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

# sample request
# http://127.0.0.1:8000/tradingdaysvalidator?db_host=localhost&db_user=root&db_password=pegasus&db_name=index_data