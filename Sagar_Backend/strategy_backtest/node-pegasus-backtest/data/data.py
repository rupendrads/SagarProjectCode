import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from typing import Any, Dict, List
from typing import Union
import pandas as pd
import mysql.connector
from datetime import datetime

def fetch_futures_data(symbol: str, start_date: Union[datetime, str] = None, end_date: Union[datetime, str] = None, type='I') -> pd.DataFrame:
    """
    Fetches futures data from a MySQL database for a given symbol and time range.

    Parameters:
        symbol (str): Symbol for which futures data is fetched.
        start_date (Union[datetime, str], optional): Start date of the time range.
        end_date (Union[datetime, str], optional): End date of the time range.

    Returns:
        pd.DataFrame: DataFrame containing futures data for the specified symbol and time range.
    """
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="pegasus",
        database="index_data"
    )
    futures_table = f"{symbol}_fut"
    
    query = f"""
        SELECT * FROM {futures_table} WHERE DATE(timestamp) BETWEEN '{start_date}' AND '{end_date}' AND expiry = '{type}'
    """

    # if start_date is not None:
    #     query += f" AND timestamp >= '{start_date}'"
    # if end_date is not None:
    #     query += f" AND timestamp <= '{end_date}'"
    print(query)
    cursor = db_connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    futures_df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

    cursor.close()
    db_connection.close()

    return futures_df




def fetch_options_data( symbol: str, start_date: Union[datetime, str], end_date: Union[datetime, str], options_type:str) -> pd.DataFrame:
    """
    Fetches options data from a MySQL database for a given symbol and time range.

    Parameters:
        start_date (Union[datetime, str]): Start date of the time range.
        end_date (Union[datetime, str]): End date of the time range.
        symbol (str): Symbol for which options data is fetched.

    Returns:
        pd.DataFrame: DataFrame containing options data for the specified symbol and time range.
    """
    # if isinstance(start_date, str):
    #     start_date = datetime.fromisoformat(start_date)
    # if isinstance(end_date, str):
    #     end_date = datetime.fromisoformat(end_date)
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="pegasus",
        database="index_data"
    )

    option_dataframes = []

    for year in range(start_date.year, end_date.year + 1):
        option_table = f"{symbol}_{year}"
        query = f"""
            SELECT timestamp, expiry, symbol, strike, type, close, expiry_type
            FROM {option_table}
            WHERE DATE(timestamp) BETWEEN '{start_date}' AND '{end_date}' AND type='{options_type}' AND expiry_type='current';
            
        """
        # print(query)
        cursor = db_connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        option_df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        option_dataframes.append(option_df)
        cursor.close()
    db_connection.close()

    result_df = pd.concat(option_dataframes, ignore_index=True)
    result_df.reset_index(inplace=True, drop=True)
    result_df.sort_values('timestamp')
    print(result_df)
    return result_df


def hello():
    print('hi')
    return 0