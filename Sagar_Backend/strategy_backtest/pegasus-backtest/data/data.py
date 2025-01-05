import asyncio
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from typing import Any, Dict, List
DataFrame = pd.DataFrame
Queue = asyncio.Queue

path = r'C:\Users\pegas\OneDrive\Desktop\indexing\index_data.db'

def fetch_data(start_date: str, end_date: str, symbol: str) -> None:
    """
    Fetch data from the database within the specified date range.

    Parameters:
        start_date (str): Start date of the data to fetch.
        end_date (str): End date of the data to fetch.
        symbol (str): Symbol or instrument to fetch data for.
        queue (Queue): Queue to store data.
    """
    print(f'Fetching data from {start_date} to {end_date}')

    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        data = []

        for year in range(pd.Timestamp(start_date).year, pd.Timestamp(end_date).year + 1):
            table_name = f'{symbol}_{year}'
            query = f'''
                    SELECT *
                    FROM {table_name}
                    WHERE timestamp BETWEEN ? AND ?
                    AND type = 'FUT'
                    AND expiry='I'
                    '''
            cursor.execute(query, (start_date, end_date))
            year_data = cursor.fetchall()
            data.extend(year_data)
        print('Fetching done')
        return data

        conn.close()
    except Exception as e:
        print(f'Error occurred while fetching data: {e}')