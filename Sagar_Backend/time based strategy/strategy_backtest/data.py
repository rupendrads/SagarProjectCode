import pandas as pd
import mysql.connector
from mysql.connector import Error
from utils import error_handler
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
db_config = fetch_parameter(environment, "dbConfig")

# @error_handler
# def get_underlying_ltp(underlying, start_time, start_date, end_date, instrument_type, implied_futures_expiry=False):
#     """
#     Fetches the last traded price (LTP) or implied futures weekly from the database for the specified underlying asset
#     between the provided start and end dates at the given start time, based on the type of instrument specified.
    
#     :param underlying: The underlying asset (e.g., 'nifty')
#     :param start_time: The time of day for the LTP or implied futures weekly (e.g., '09:30:00')
#     :param start_date: The starting date of the query range (e.g., '2023-01-01')
#     :param end_date: The ending date of the query range (e.g., '2023-01-31')
#     :param instrument_type: Type of instrument ('futures' for futures, 'implied' for implied futures weekly)
#     :return: A DataFrame containing the timestamps and respective values based on instrument type.
#     """
#     print("fetching data")
#     if instrument_type not in ["futures", "spot"]:
#         if implied_futures_expiry == 0:
#             field = "implied_futures_weekly"
#         else:
#             field = "implied_futures_monthly"
#         table_name = f"{db_config['database']}.{underlying}_fut"
#     else:
#         if instrument_type == "futures":
#             table_name = f"{db_config['database']}.{underlying}_fut"
#         else:
#             table_name = f"{db_config['database']}.{underlying}_index"
#         field = "open"

#     try:
#         conn = mysql.connector.connect(**db_config)
#         if conn.is_connected():
#             cursor = conn.cursor()
#             if instrument_type == "spot":
#                 query = f"""
#                 SELECT timestamp, {field}
#                 FROM {table_name}
#                 WHERE time(timestamp) = '{start_time}'
#                 AND date(timestamp) BETWEEN '{start_date}' AND '{end_date}'
#                 """
#             else:
#                 query = f"""
#                 SELECT timestamp, {field}
#                 FROM {table_name}
#                 WHERE time(timestamp) = '{start_time}'
#                 AND date(timestamp) BETWEEN '{start_date}' AND '{end_date}'
#                 AND expiry = 'I'
#                 """
#             print(query)
#             cursor.execute(query)
#             data = cursor.fetchall()
#             df = pd.DataFrame(data, columns=['timestamp', 'close'])
#             df.sort_values('timestamp', inplace=True)
#             return df
#     except Error as e:
#         print(f"Error: {e}")
#     finally:
#         if conn.is_connected():
#             cursor.close()
#             conn.close()

@error_handler
def get_expiry_df(underlying, start_date, end_date, entry_time, exit_time):
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            cursor = conn.cursor()
            start_year = int(start_date.split('-')[0])
            end_year = int(end_date.split('-')[0])
            years = list(range(start_year, end_year + 1))
            all_data = pd.DataFrame()

            for year in years:
                table_name = f"{underlying}_{year}"
                query = f"""
                SELECT timestamp, symbol, open, high, low, close, expiry, type, strike
                FROM {db_config['database']}.{table_name}
                WHERE date(timestamp) BETWEEN '{start_date}' AND '{end_date}'
                AND time(timestamp) BETWEEN '{entry_time}' AND '{exit_time}'
                """
                print(query)
                cursor.execute(query)
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'expiry', 'type', 'strike'])
                all_data = pd.concat([all_data, df])

            all_data.sort_values(['symbol', 'timestamp'], inplace=True)
            # print(all_data)
            return all_data
    except Error as e:
        print(f"Error {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
def filter_dataframe_by_time(df, start_time):
    """
    Filters a DataFrame based on the start_time in the 'timestamp' column.
    
    :param df: Input DataFrame containing a 'timestamp' column with datetime values.
    :param start_time: The start time as a string (e.g., '09:30:00').
    :return: Filtered DataFrame
    """
    try:
        # Ensure the 'timestamp' column is converted to datetime if not already
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')

        # Convert start_time to a time object including seconds
        start_time_obj = pd.to_datetime(start_time, format='%H:%M:%S').time()

        # Filter the DataFrame to match the start_time
        filtered_df = df[df['timestamp'].dt.time == start_time_obj]

        return filtered_df

    except Exception as e:
        print(f"Error: {e} in filter_dataframe_by_time function")

def get_underlying_ltp(underlying, start_date, end_date, instrument_type, implied_futures_expiry=False):
    """
    Fetches the last traded price (LTP) or implied futures weekly from the database for the specified underlying asset
    between the provided start and end dates, based on the type of instrument specified.
    
    :param underlying: The underlying asset (e.g., 'nifty')
    :param start_date: The starting date of the query range (e.g., '2023-01-01')
    :param end_date: The ending date of the query range (e.g., '2023-01-31')
    :param instrument_type: Type of instrument ('futures' for futures, 'implied' for implied futures weekly)
    :return: A DataFrame containing the timestamps and respective values based on instrument type.
    """
    print("Fetching data")
    if instrument_type not in ["futures", "spot"]:
        if implied_futures_expiry == 0:
            field = "implied_futures_weekly"
        else:
            field = "implied_futures_monthly"
        table_name = f"{db_config['database']}.{underlying}_fut"
    else:
        if instrument_type == "futures":
            table_name = f"{db_config['database']}.{underlying}_fut"
        else:
            table_name = f"{db_config['database']}.{underlying}_index"
        field = "open"

    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            cursor = conn.cursor()
            query = f"""
            SELECT timestamp, {field}
            FROM {table_name}
            WHERE date(timestamp) BETWEEN '{start_date}' AND '{end_date}'
            """
            print(query)
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['timestamp', 'close'])
            df.sort_values('timestamp', inplace=True)
            return df
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@error_handler
def get_underlying_ltp(underlying, start_date, end_date, instrument_type, implied_futures_expiry=False):
    """
    Fetches the last traded price (LTP) or implied futures weekly from the database for the specified underlying asset
    between the provided start and end dates, based on the type of instrument specified.
    
    :param underlying: The underlying asset (e.g., 'nifty')
    :param start_date: The starting date of the query range (e.g., '2023-01-01')
    :param end_date: The ending date of the query range (e.g., '2023-01-31')
    :param instrument_type: Type of instrument ('futures' for futures, 'implied' for implied futures weekly)
    :return: A DataFrame containing the timestamps and respective values based on instrument type.
    """
    print("fetching data")
    if instrument_type not in ["futures", "spot"]:
        if implied_futures_expiry == 0:
            field = "implied_futures_weekly"
        else:
            field = "implied_futures_monthly"
        table_name = f"{db_config['database']}.{underlying}_fut"
    else:
        if instrument_type == "futures":
            table_name = f"{db_config['database']}.{underlying}_fut"
        else:
            table_name = f"{db_config['database']}.{underlying}_index"
        field = "open"

    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            cursor = conn.cursor()
            if instrument_type == "spot":
                query = f"""
                SELECT timestamp, {field}
                FROM {table_name}
                WHERE date(timestamp) BETWEEN '{start_date}' AND '{end_date}'
                """
            else:
                query = f"""
                SELECT timestamp, {field}
                FROM {table_name}
                WHERE date(timestamp) BETWEEN '{start_date}' AND '{end_date}'
                AND expiry = 'I'
                """
            print(query)
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['timestamp', 'close'])
            df.sort_values('timestamp', inplace=True)
            return df
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
