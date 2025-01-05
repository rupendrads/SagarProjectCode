import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import pandas as pd
from dateutil import parser
import json
import os
import math
from datetime import date
import gzip
import shutil
import glob
from collections import defaultdict
import functools
import warnings
import re
import numpy as np
from typing import Any
import logging
import datetime as dt
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
charges = fetch_parameter(environment, "charges")



warnings.simplefilter(action='ignore', category=FutureWarning)
"""
 Logger Class
 """
class Logger:
    def __init__(self, filename):
        self.filename = filename

    def log(self, message):
        with open(self.filename, 'a') as file:
            file.write(f"{message}\n")
pegasus = Logger('utils.txt')
"""
this function takes any value and round it off to nearest 0.05
for example:
price = 8.123, u will get resultant as 8.1 (as 8.123 is closer to 8.1 than 8.15)
"""

def round_to_tick(price: float, tick_size: float = 0.05) -> float:
    return round(round(price / tick_size) * tick_size, 2)


def calculate_charges(buyprice, qty, sellprice, brokerageCost=20):  # default brokerageCost is assumed to be 20
    calcparams = {}
    calcparams['buyprice'] = buyprice
    calcparams['sellprice'] = sellprice
    calcparams['qty'] = qty

    calcparams['buyturnover'] = buyprice * qty
    calcparams['sellturnover'] = sellprice * qty
    calcparams['Turnover'] = calcparams['buyturnover'] + calcparams['sellturnover']

    calcparams['brokerage'] = 2 * brokerageCost  # Fixed brokerage cost

    # STT sell side (on premium) and CTT buy side are applicable
    calcparams['STT'] = calcparams['sellturnover'] * charges['stt'] / 100
    calcparams['ExcTranTax'] = calcparams['Turnover'] * (charges['exchangeTransactionCharge'] / 100)
    calcparams['SEBIchg'] = (calcparams['Turnover']) * (charges['sebiCharge'] / 100)
    calcparams['ipft'] = ((calcparams['Turnover'] // 10000000)+1) * charges['ipft']
    calcparams['GST'] = (calcparams['brokerage'] + calcparams['SEBIchg'] + calcparams['ExcTranTax']) * 18 / 100
    calcparams['StampDuty'] = (calcparams['buyturnover'] * (charges['stampDuty']) / 100)

    # Total Charges (OtherCharges is everything except brokerage)
    calcparams['OtherCharges'] = calcparams['STT'] + calcparams['ExcTranTax'] + calcparams['SEBIchg'] + calcparams['GST'] + calcparams['StampDuty'] + calcparams['ipft']

    # Debug prints for each charge
    # print(f"Buy Turnover: {calcparams['buyturnover']}")
    # print(f"Sell Turnover: {calcparams['sellturnover']}")
    # print(f"Total Turnover: {calcparams['Turnover']}")
    # print(f"Brokerage: {calcparams['brokerage']}")
    # print(f"STT: {calcparams['STT']}")
    # print(f"ExcTranTax: {calcparams['ExcTranTax']}")
    # print(f"SEBI Charges: {calcparams['SEBIchg']}")
    # print(f"IPFT: {calcparams['ipft']}")
    # print(f"GST: {calcparams['GST']}")
    # print(f"Stamp Duty: {calcparams['StampDuty']}")
    # print(f"Other Charges: {calcparams['OtherCharges']}")

    return {'brokerage': calcparams['brokerage'], 'otherCharges': calcparams['OtherCharges']}


def apply_charges(row):
    if row['trade'] == 'buy':
        buyprice = row['entry_price']
        sellprice = row['exit_price']
    else:
        buyprice = row['exit_price']
        sellprice = row['entry_price']
    qty = row['qty']
    return calculate_charges(buyprice, qty, sellprice)



def apply_charges_api(row, brokerageCost):
    if row['trade'] == 'buy':
        buyprice = row['entry_price']
        sellprice = row['exit_price']
    else:
        buyprice = row['exit_price']
        sellprice = row['entry_price']
    qty = row['qty']
    brokerageCost = int(brokerageCost)
    return calculate_charges_api(buyprice, qty, sellprice, brokerageCost)

def calculate_charges_api(buyprice, qty, sellprice, brokerageCost=20):
    calcparams = {}
    calcparams['buyprice'] = buyprice
    calcparams['sellprice'] = sellprice
    calcparams['qty'] = qty
    calcparams['buyturnover'] = buyprice * qty
    calcparams['sellturnover'] = sellprice * qty
    calcparams['Turnover'] = calcparams['buyturnover'] + calcparams['sellturnover']
    calcparams['brokerage'] = 2 * brokerageCost
    calcparams['STT'] = calcparams['sellturnover'] * charges['stt'] / 100
    calcparams['ExcTranTax'] = calcparams['Turnover'] * (charges['exchangeTransactionCharge'] / 100)
    calcparams['SEBIchg'] = (calcparams['Turnover']) * (charges['sebiCharge'] / 100)
    calcparams['ipft'] = ((calcparams['Turnover'] // 10000000)+1) * charges['ipft']
    calcparams['GST'] = (calcparams['brokerage'] + calcparams['SEBIchg'] + calcparams['ExcTranTax']) * 18 / 100
    calcparams['StampDuty'] = (calcparams['buyturnover'] * (charges['stampDuty']) / 100)
    calcparams['OtherCharges'] = calcparams['STT'] + calcparams['ExcTranTax'] + calcparams['SEBIchg'] + calcparams['GST'] + calcparams['StampDuty'] + calcparams['ipft']
    return {'brokerage': calcparams['brokerage'], 'otherCharges': calcparams['OtherCharges']}
    
def record_tradebook(tradebook, entry_price, entry_time, exit_price, exit_time, pnl):
    
    new_record = {
        'entry_price': entry_price,
        'entry_timestamp': entry_time,
        'exit_price': exit_price,
        'exit_timestamp': exit_time,
        'pnl': pnl
    }

    """
    This function processes the NSE FO contract CSV files and updates the lot sizes in a JSON file.
    
    Steps:
    1. Checks if the 'lot_sizes.json' file has already been updated for the day. If it has, the function exits early.
    2. Searches for any matching CSV.gz files in the current working directory.
    3. If a matching file is found, it is unzipped and saved as a CSV file.
    4. The CSV file is read and processed to extract 'TckrSymb' and 'NewBrdLotQty' columns.
    5. The processed data is saved in 'lot_sizes.json' in the format {"symbol": "lot_size"}.
    6. If no matching file is found, it prompts the user to upload the contract file zip.
    
    The function ensures that the JSON file is not updated more than once per day.
    """
def process_nfo_lot_file():
    json_file_path = os.path.join(os.getcwd(), 'lot_sizes.json')
    if os.path.exists(json_file_path):
        json_mod_time = datetime.fromtimestamp(os.path.getmtime(json_file_path))
        if json_mod_time.date() == datetime.now().date():
            print(f"JSON file has already been updated for today")
            return
    matching_files = glob.glob(os.path.join(os.getcwd(), "NSE_FO_contract_*.csv.gz"))
    if matching_files:
        file_path = matching_files[0]
        file_name = os.path.basename(file_path)
        print(f"Found file: {file_name}")

        try:
            with gzip.open(file_path, 'rb') as f_in:
                output_name = os.path.splitext(file_name)[0]
                output_path = os.path.join(os.getcwd(), output_name)
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"Unzipped file saved to: {output_path}")
            df = pd.read_csv(output_path)
            df = df[["TckrSymb", "NewBrdLotQty"]]
            df.columns = ["symbol", "lot_size"]
            df = df.drop_duplicates(subset="symbol")
            df_dict = df.set_index('symbol').to_dict()['lot_size']
            with open(json_file_path, 'w') as json_file:
                json.dump(df_dict, json_file, indent=4)
            print(f"JSON file updated: {json_file_path}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
    else:
        print("No contract file found. Please upload the contract file zip.")

"""
    A decorator function to handle exceptions in the decorated function.
    
    This decorator wraps a function and catches any exceptions that occur during 
    its execution. If an exception is caught, it prints an error message including 
    the name of the function where the error occurred and the error message.

    Parameters:
    func (function): The function to be wrapped by the decorator.

    Returns:
    function: The wrapped function with error handling.
    """
def error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            method_name = func.__name__
            print(f"{method_name} Error: {e}")
    return wrapper
"""
    Processes strategy CSV files within a specified root folder, optionally considering 
    square-off conditions based on stop-loss hits.

    This function iterates through subdirectories of the root folder, reading strategy CSV files,
    combining their PnL (Profit and Loss) data, and saving the combined results back to the subdirectory.
    If the 'squareoff' parameter is set to 'complete', the function also checks for the earliest stop-loss 
    hit and adjusts the combined PnL data accordingly.

    Parameters:
    root_folder (str): The path to the root folder containing strategy subdirectories.
    squareoff (str): Specifies whether to consider complete square-off conditions ('complete') 
                     or not ('partial'). Default is 'partial'.

    Steps:
    1. Iterate through each item in the root folder.
    2. For each subdirectory with a date-formatted name, initialize combined PnL data and 
       variables to track the earliest stop-loss hit.
    3. Iterate through each CSV file in the subdirectory:
       a. Read the CSV file into a DataFrame.
       b. Extract the 'timestamp' and 'pnl' columns.
       c. If 'squareoff' is 'complete', identify the earliest stop-loss hit based on 'remark' column.
       d. Combine the PnL data from the current file with the aggregated PnL data.
    4. If an earliest stop-loss hit is identified, filter the combined PnL data up to that timestamp.
    5. Save the combined PnL data to a new CSV file in the subdirectory.
"""


def read_strategy_folder(root_folder, squareoff="partial"):
    print(f"Strategy squareoff is {squareoff}")
    for item in os.listdir(root_folder): 
        item_path = os.path.join(root_folder, item)
        print(f"item path is {item_path}")
        
        if os.path.isdir(item_path) and is_date_format(item):
            combined_leg_pnl = None
            earliest_sl_hit_timestamp = None
            earliest_sl_hit_file = None
            
            for file_name in os.listdir(item_path):
                file_path = os.path.join(item_path, file_name)
                
                if file_name.endswith('.csv'):
                    strategy_df = pd.read_csv(file_path)
                    print(f"Read file: {file_path}")
                    
                    leg_pnl = strategy_df[['timestamp', 'pnl']]
                    
                    if squareoff == 'complete' and 'remark' in strategy_df.columns:
                        sl_hit_rows = strategy_df[strategy_df['remark'].str.contains('sl_hit', na=False)]
                        if not sl_hit_rows.empty:
                            sl_hit_timestamp = sl_hit_rows['timestamp'].iloc[0]
                            if earliest_sl_hit_timestamp is None or sl_hit_timestamp < earliest_sl_hit_timestamp:
                                earliest_sl_hit_timestamp = sl_hit_timestamp
                                earliest_sl_hit_file = file_name
                    
                    if combined_leg_pnl is None:
                        combined_leg_pnl = leg_pnl
                    else:
                        combined_leg_pnl = combined_leg_pnl.merge(
                            leg_pnl, on='timestamp', how='outer', suffixes=('', '_y')
                        )
                        combined_leg_pnl['pnl'] = combined_leg_pnl['pnl'].fillna(0) + combined_leg_pnl['pnl_y'].fillna(0)
                        combined_leg_pnl.drop(columns=['pnl_y'], inplace=True)
            
            if earliest_sl_hit_timestamp:
                # print(f"Earliest SL hit in file: {earliest_sl_hit_file} at timestamp: {earliest_sl_hit_timestamp}")
                for file_name in os.listdir(item_path):
                    file_path = os.path.join(item_path, file_name)
                    
                    if file_name.endswith('.csv'):
                        strategy_df = pd.read_csv(file_path)
                        trimmed_df = strategy_df[strategy_df['timestamp'] <= earliest_sl_hit_timestamp]
                        trimmed_df.to_csv(file_path, index=False)
                        print(f"Trimmed and saved {file_name} to {file_path}")
                
                combined_leg_pnl = combined_leg_pnl[combined_leg_pnl['timestamp'] <= earliest_sl_hit_timestamp]
            
            if combined_leg_pnl is not None:
                combined_leg_pnl = combined_leg_pnl.sort_values('timestamp').reset_index(drop=True)
                output_file_path = os.path.join(item_path, f"combined_leg_pnl_{item}.csv")
                combined_leg_pnl.to_csv(output_file_path, index=False)
                # print(f"Saved combined PnL for {item} to {output_file_path}")
                print(f"----------------------------")
                # print(combined_leg_pnl)
            else:
                print(f"No PnL data found for {item}")


"""
This function returns True if the date_string is a date else False
"""
def is_date_format(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

"""
This function takes dataframe, timestamp, file_name and folder name and save them appropriately.
"""
def save_df_with_date(df, timestamp, base_filename, folder_name):
    df_date = timestamp.strftime('%Y-%m-%d')
    date_folder = os.path.join(folder_name, df_date)
    os.makedirs(date_folder, exist_ok=True)
    filename = os.path.join(date_folder, f"{base_filename}__minutewise_{df_date}.csv")
    df.to_csv(filename, index=False)
    

"""
    Maps the given index name to a corresponding shorthand identifier.

    This function takes an index name as input and returns a corresponding shorthand identifier 
    based on a predefined mapping. The input index name is case-insensitive.

    Parameters:
    index_name (str): The name of the index to be mapped.

    Returns:
    str or None: The shorthand identifier if the index name is found in the mapping, otherwise None.

    Index Mapping:
    --------------
    'NIFTY 50'         -> 'nifty'
    'NIFTY BANK'       -> 'banknifty'
    'NIFTY FIN SERVICE' -> 'finnifty'
    'NIFTY MIDCAP 50'  -> 'midcpnifty'
"""
def assign_index(index_name):
    index_mapping = {
        'NIFTY 50': 'nifty',
        'NIFTY BANK': 'banknifty',
        'NIFTY FIN SERVICE': 'finnifty',
        'NIFTY MIDCAP 50': 'midcpnifty'
    }
    
    index_name = index_name.upper()  
    return index_mapping.get(index_name, None)
"""
    Calculates the At-The-Money (ATM) strike price for options trading.

    This function takes the current price of an underlying asset and a strike_interval value, 
    and calculates the ATM strike price by rounding the price to the nearest multiple 
    of the strike_interval value.

    Parameters:
    price (float): The current price of the underlying asset.
    strike_interval (int or float): The strike_interval value to which the price should be rounded.

    Returns:
    int or float: The ATM strike price rounded to the nearest multiple of the strike_interval value.

    Example Usage:
    --------------
    get_atm_strike(10432, 50)    # Returns 10450
    get_atm_strike(2987, 100)    # Returns 3000
"""

"""
This function takes price and strike_interval to determine the ATM (at the money) value of the price.
"""
def get_atm_strike(price, strike_interval):
    # print(price, strike_interval)
    return  round(price / strike_interval) * strike_interval

"""
    Processes a df of trade book data to fill in minute-wise PnL (Profit and Loss) values.

    This function takes a df containing trade book data with timestamps and PnL values,
    and processes it to ensure there are minute-wise entries from the specified start time to
    the end time. It fills in missing PnL values by forward-filling for continuity of
    PnL values across gaps in the data.

    Parameters:
    df (DataFrame): The input df containing 'timestamp' and 'pnl' columns.
    start_time (str): The start time in 'HH:MM' format.
    end_time (str): The end time in 'HH:MM' format.

    Returns:
    DataFrame: A df with minute-wise 'timestamp' and 'pnl' values filled in and adjusted.

    Steps:
    1. Convert the 'timestamp' column to datetime format.
    2. Determine the base date from the earliest timestamp in the df.
    3. Create datetime objects for the start and end times based on the base date.
    4. Sort the df by 'timestamp'.
    5. Fill any missing 'pnl' values with 0.
    6. Segment the df into continuous blocks of minute-wise data.
    7. Adjust PnL values across segments to ensure continuity.
    8. Reindex the df to include all minute-wise timestamps from start to end time.
    9. Forward-fill and backfill missing PnL values.
    10. Round the 'pnl' values to 2 decimal places and return the processed df.
"""
logging.basicConfig(filename='continuous_position.txt', 
                    level=logging.INFO, 
                    format='%(message)s',
                    filemode='a')  # 'a' for append mode
def process_minutewise_tradebook(df, start_time, end_time, qty):
    
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        base_date = df['timestamp'].min().date()
        start_datetime = pd.to_datetime(f"{base_date} {start_time}")
        end_datetime = pd.to_datetime(f"{base_date} {end_time}")
        
        df.sort_values('timestamp', inplace=True)
        sl_hit_pnl = 0
        add_pnl = False  # Initialize flag to track if pnl should be added
        counter = 0
        for i in range(1, len(df)):
            counter +=1
            time_diff = (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 60

            # Check if sl_hit condition is met and time difference is 1 minute
            if df.iloc[i-1]['remark'] == 'sl_hit' and time_diff == 1:
                sl_hit_pnl = df.iloc[i-1]['pnl']  # Store pnl at sl_hit
                add_pnl = True  # Assume we need to add pnl
                # logging.info(f"Previous row (sl_hit): {df.iloc[i-1].to_dict()}")

                # Track whether the next sequence of remarks ends with 'position_roll'
                end_with_position_roll = False
                
                # Check if subsequent rows are 'none' and end with 'position_roll'
                for j in range(i, len(df)):
                    if df.iloc[j]['remark'] == 'position_roll':
                        end_with_position_roll = True
                        logging.info(f"Remark ends with 'position_roll' at row {j}: {df.iloc[j].to_dict()} and counter {counter}")
                        break
                    elif df.iloc[j]['remark'] != 'none':
                        # logging.info(f"Remark changed from 'none' at row {j}: {df.iloc[j].to_dict()}")
                        end_with_position_roll = False
                        break
                
                # If it ends with 'position_roll', don't add pnl
                if end_with_position_roll:
                    # logging.info(f"Skipping pnl addition due to 'position_roll' ending.")
                    add_pnl = False  # Skip adding pnl entirely

            if add_pnl:
                df.at[i, 'pnl'] += sl_hit_pnl
                # logging.info(f"Accumulated pnl added to row: {df.iloc[i].to_dict()}")

                # If any remark other than 'none' is encountered, stop adding pnl
                if df.iloc[i]['remark'] not in ['none']:
                    # logging.info(f"Remark changed, stopping pnl addition: {df.iloc[i].to_dict()}")
                    add_pnl = False

        df['pnl'] = df['pnl'].fillna(0)
        last_pnl = 0
        segments = []
        current_segment = []

        for i in range(len(df)):
            if i > 0 and (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 60 > 1:
                segments.append(current_segment)
                current_segment = []
            current_segment.append(df.iloc[i])
        if current_segment:
            segments.append(current_segment)
        
        for i in range(1, len(segments)):
            end_pnl = segments[i-1][-1]['pnl']
            for j in range(len(segments[i])):
                segments[i][j]['pnl'] += end_pnl
        
        df = pd.DataFrame([item for sublist in segments for item in sublist])
        complete_time_range = pd.date_range(start=start_datetime, end=end_datetime, freq='min')
        
        df.set_index('timestamp', inplace=True)
        df = df.reindex(complete_time_range)
        
        df.ffill(inplace=True)
        df.fillna(0, inplace=True)
        
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'timestamp'}, inplace=True)
        df['pnl'] = round(df['pnl'], 2)
        df['qty'] = qty
        return df
    except Exception as e:
        print(f"Error in process_minutewise_tradebook: {e}")

# def process_minutewise_tradebook(df, start_time, end_time):
#     try:
#         df['timestamp'] = pd.to_datetime(df['timestamp'])
#         base_date = df['timestamp'].min().date()
#         start_datetime = pd.to_datetime(f"{base_date} {start_time}")
#         end_datetime = pd.to_datetime(f"{base_date} {end_time}")
        
#         df.sort_values('timestamp', inplace=True)
        
#         df['pnl'] = df['pnl'].fillna(0)
#         last_pnl = 0
#         segments = []
#         current_segment = []

#         for i in range(len(df)):
#             if i > 0 and (df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']).total_seconds() / 60 > 1:
#                 segments.append(current_segment)
#                 current_segment = []
#             current_segment.append(df.iloc[i])
#         if current_segment:
#             segments.append(current_segment)
        
#         for i in range(1, len(segments)):
#             end_pnl = segments[i-1][-1]['pnl']
#             for j in range(len(segments[i])):
#                 segments.loc[i,j]['pnl'] += end_pnl
        
#         df = pd.DataFrame([item for sublist in segments for item in sublist])
        
#         complete_time_range = pd.date_range(start=start_datetime, end=end_datetime, freq='min')
        
#         df.set_index('timestamp', inplace=True)
#         df = df.reindex(complete_time_range)
        
#         df.ffill(inplace=True)
#         df.fillna(0, inplace=True)
        
#         df.reset_index(inplace=True)
#         df.rename(columns={'index': 'timestamp'}, inplace=True)
#         df['pnl'] = round(df['pnl'],2)
#         return df
#     except Exception as e:
#         print(f"error in process_minutewise_tradebook {e}")

"""
    Extracts and returns the current, next, and monthly expiry dates from the given DataFrame.

    This function processes a DataFrame containing expiry dates, identifies the current and next expiry dates,
    and determines the monthly expiry date based on a predefined rule.

    Parameters:
    df (DataFrame): The input DataFrame containing an 'expiry' column with expiry dates.

    Returns:
    tuple: A tuple containing the current expiry date, next expiry date, and monthly expiry date.

    Raises:
    ValueError: If the input DataFrame is empty.

"""

def get_expiry_list(df):
    print(f"get expiry list method is being called")
    if not df.empty:
        expiry_list = list(set(df['expiry']))
        expiry_list.sort()
        current_expiry = expiry_list[0]
        # return current_expiry, None, None
        next_expiry = expiry_list[1]
        monthly_expiry_list = get_last_expiry(expiry_list)
        monthly_expiry = monthly_expiry_list[1] if current_expiry == monthly_expiry_list[0] else monthly_expiry_list[0]
        print(current_expiry, next_expiry, monthly_expiry)
        return current_expiry, next_expiry, monthly_expiry
    else:
        raise ValueError("couldnt find expiry for the given expiry dataframe")

    

"""
    Processes PnL files in the specified root folder based on specified conditions.
    This function iterates through subdirectories of the root folder, identifies and reads combined PnL CSV files,
    and processes them to create final PnL files. The processing stops at the point where either a specified maximum
    profit or maximum loss is reached. The resulting PnL data is saved into new CSV files.

    Parameters:
    root_folder (str): The path to the root folder containing strategy subdirectories.
    max_profit (float or bool): The maximum profit threshold. If False, it is not considered. Default is False.
    max_loss (float or bool): The maximum loss threshold. If False, it is not considered. Default is False.
    squareoff (str): Specifies the square-off condition. Default is "partial".

    Returns:
    None
"""
# def process_pnl_files(root_folder, max_profit=False, max_loss=False, squareoff="partial", trail_sl={"priceMove": 300, "sl_adjustment": 50}):
#     print(f"Processing files with max profit: {max_profit}, max loss: {max_loss}, trailing SL: {trail_sl}")
    
#     if max_profit is False and max_loss is False:
#         print("Overall profit and overall loss are not specified")
#         return

#     for item in os.listdir(root_folder):
#         item_path = os.path.join(root_folder, item)
        
#         if os.path.isdir(item_path) and is_date_format(item):
#             for file_name in os.listdir(item_path):
#                 if file_name.startswith('combined_leg_pnl') and file_name.endswith('.csv'):
#                     file_path = os.path.join(item_path, file_name)
#                     pnl_df = pd.read_csv(file_path)
#                     cut_index = None
#                     trailing_max_loss = max_loss  

#                     for i, pnl in enumerate(pnl_df['pnl']):
#                         if max_profit is not False and pnl >= max_profit:
#                             cut_index = i
#                             break
                        
#                         if trail_sl and max_loss is not False and pnl >= trail_sl['priceMove']:
#                             move_steps = pnl // trail_sl['priceMove']  
#                             trailing_max_loss = max_loss + move_steps * trail_sl['sl_adjustment']
#                             print(f"Trailing stop loss adjusted to: {trailing_max_loss}")

#                         if trailing_max_loss is not False and pnl <= trailing_max_loss:
#                             cut_index = i
#                             break
                    
#                     if cut_index is not None:
#                         final_pnl_df = pnl_df.iloc[:cut_index + 1]
#                         final_file_name = f"final_{file_name}"
#                         final_file_path = os.path.join(item_path, final_file_name)
#                         final_pnl_df.to_csv(final_file_path, index=False)
#                         print(f"Saved final df as {final_file_path}")

def process_strategy_constraints(strategy):
    root_folder = strategy.name
    max_profit_hit = "strategy_max_profit_hit"
    max_loss_hit = "strategy_max_loss_hit"
    
    for file_name in os.listdir(root_folder):
        if file_name.endswith('_combined_pnl.csv'):
            combined_pnl_file = os.path.join(root_folder, file_name)
            pnl_df = pd.read_csv(combined_pnl_file)
            common_prefix = file_name.split('_')[0]
            
            pnl_df['entry_timestamp'] = pd.to_datetime(pnl_df['entry_timestamp'])
            pnl_df['exit_timestamp'] = pd.to_datetime(pnl_df['exit_timestamp'])
            grouped_pnl = pnl_df.groupby(pnl_df['entry_timestamp'].dt.date)

            for day, day_trades in grouped_pnl:
                day_folder = os.path.join(root_folder, day.strftime('%Y-%m-%d'))
                if os.path.exists(day_folder):
                    for minute_file in os.listdir(day_folder):
                        if minute_file.startswith(f"{common_prefix}__minutewise") and minute_file.endswith('.csv'):
                            minute_file_path = os.path.join(day_folder, minute_file)
                            minutewise_df = pd.read_csv(minute_file_path)
                            # print(minutewise_df)
                            minutewise_df['timestamp'] = pd.to_datetime(minutewise_df['timestamp'])

                            hit_row = minutewise_df[minutewise_df['remark'].isin([max_profit_hit, max_loss_hit])]
                            if not hit_row.empty:
                                cut_timestamp = hit_row['timestamp'].iloc[0]
                                cut_price = hit_row['close'].iloc[0]
                                cut_pnl = hit_row['pnl'].iloc[0]
                                remark = hit_row['remark'].iloc[0]

                                for idx, trade in day_trades.iterrows():
                                    #fixing exceptional cases where the trade will enter and exit on the same timestamp by using <= instead of <
                                    if trade['entry_timestamp'] <= cut_timestamp <= trade['exit_timestamp']:
                                        pnl_df.at[idx, 'exit_timestamp'] = cut_timestamp
                                        pnl_df.at[idx, 'exit_price'] = cut_price
                                        pnl_df.at[idx, 'pnl'] = cut_pnl
                                        pnl_df.at[idx, 'remark'] = remark
                                    elif trade['entry_timestamp'] >= cut_timestamp:
                                        pnl_df = pnl_df.drop(idx)

            pnl_df.to_csv(combined_pnl_file, index=False)

def update_tradebook_with_pnl(tradebook, strategy, column_name = 'trade'):
    print("-----------------------update_tradebook_with_pnl----------")
    qty_column = 'quantity' if 'quantity' in tradebook.columns else 'qty'
    print(tradebook)
    if not tradebook.empty:
        tradebook['entry_price'] = round(tradebook['entry_price'], 2)
        tradebook['exit_price'] = round(tradebook['exit_price'], 2)
        tradebook['sl'] = round(tradebook['sl'], 2)
        for idx, row in tradebook.iterrows():
            if row[column_name].upper() == 'BUY':
                tradebook.at[idx, 'pnl'] = round((row['exit_price'] - row['entry_price'])*row[qty_column], 2)
            else:
                tradebook.at[idx, 'pnl'] = round((row['entry_price'] - row['exit_price'])*row[qty_column], 2)

    return tradebook


def process_pnl_files(strategy):
    root_folder = strategy.name
    # print(f"processing files {strategy.overall_target}, {strategy.overall_sl}")
    if strategy.overall_target is False and strategy.overall_sl is False:
        # print("Overall profit and overall loss are not specified")
        pegasus.log("Overall profit and overall loss are not specified")
        return
    max_profit = strategy.overall_target
    max_loss = -strategy.overall_sl
    for item in os.listdir(root_folder):
        item_path = os.path.join(root_folder, item)
        
        if os.path.isdir(item_path) and is_date_format(item):
            cut_timestamp = None
            cut_pnl_value = None
            combined_pnl_file = None
            note = None
            for file_name in os.listdir(item_path):
                if file_name.startswith('combined_leg_pnl') and file_name.endswith('.csv'):
                    combined_pnl_file = os.path.join(item_path, file_name)
                    pnl_df = pd.read_csv(combined_pnl_file)
                    if strategy.trailing_for_strategy is not False:
                        # print('trailing sl is applied for the strategy')
                        # pegasus.log('trailing sl is applied for the strategy')
                        if strategy.trailing_for_strategy['trail_type'] == 'lock':
                            trail_sl = 0
                            set_trail_sl = False
                            for i, (timestamp, pnl) in enumerate(zip(pnl_df['timestamp'], pnl_df['pnl'])):
                                trail_multiplier = pnl//strategy.trailing_for_strategy['priceMove']
                                if (trail_multiplier > 0) and (not set_trail_sl):
                                    trail_sl = strategy.trailing_for_strategy['sl_adjustment']
                                    # print(f"trail sl adjusted to {trail_sl} because current pnl is {pnl} for {timestamp}")
                                    pegasus.log(f"trail sl adjusted to {trail_sl} because current pnl is {pnl} for {timestamp}")
                                    set_trail_sl = True
                                if (pnl < trail_sl) and (set_trail_sl):
                                    cut_timestamp = timestamp
                                    cut_pnl_value = pnl
                                    # print(f"trailing sl got hit for the strategy @ {timestamp} @ {pnl}")
                                    pegasus.log(f"trailing sl got hit for the strategy @ {timestamp} @ {pnl}")
                                    note = "strategy_max_loss_hit"
                                    break
                                if strategy.overall_target  and pnl >= strategy.overall_target:
                                    cut_timestamp = timestamp
                                    cut_pnl_value = pnl
                                    # print(f"overall target got hit for the strategy @ {timestamp} @ {pnl}")
                                    pegasus.log(f"overall target got hit for the strategy @ {timestamp} @ {pnl}")
                                    note = "strategy_max_profit_hit"
                                    break
                                if strategy.overall_sl and pnl <= -strategy.overall_sl:
                                    cut_timestamp = timestamp
                                    cut_pnl_value = pnl
                                    # print(f"overall sl got hit for the strategy @ {timestamp} @ {pnl}")
                                    pegasus.log(f"overall sl got hit for the strategy @ {timestamp} @ {pnl}")
                                    note = "strategy_max_loss_hit"
                                    break

                        elif strategy.trailing_for_strategy['trail_type'] == 'lock_and_trail':
                            set_locked_trail_sl = False
                            locked_trail_sl = 0
                            trail_sl = 0
                            
                            for i, (timestamp, pnl) in enumerate(zip(pnl_df['timestamp'], pnl_df['pnl'])):
                                trail_multiplier = pnl//strategy.trailing_for_strategy['lock_adjustment']['priceMove']
                                if (trail_multiplier > 0) and (not set_locked_trail_sl):
                                    locked_trail_sl = strategy.trailing_for_strategy['lock_adjustment']['sl_adjustment']
                                    trail_sl = locked_trail_sl 
                                    pegasus.log(f"first lock and trail sl adjusted to {trail_sl} because current pnl is {pnl} for {timestamp}")
                                    set_locked_trail_sl = True
                                if set_locked_trail_sl:
                                    trail_level = pnl - strategy.trailing_for_strategy['lock_adjustment']['priceMove']#locked_trail_sl
                                    # pegasus.log(f"trail level is {trail_level} in lock&trail and trail_sl is {trail_sl} and new trail_sl calculation is {round((trail_level//strategy.trailing_for_strategy['lock_adjustment']['trail_sl_adjustment'])*strategy.trailing_for_strategy['lock_adjustment']['trail_priceMove'],2)}")
                                    if trail_level >= strategy.trailing_for_strategy['lock_adjustment']['trail_priceMove']:
                                        if trail_sl < locked_trail_sl + round((trail_level//strategy.trailing_for_strategy['lock_adjustment']['trail_priceMove'])*strategy.trailing_for_strategy['lock_adjustment']['trail_sl_adjustment'],2):
                                            trail_sl = locked_trail_sl + round((trail_level//strategy.trailing_for_strategy['lock_adjustment']['trail_priceMove'])*strategy.trailing_for_strategy['lock_adjustment']['trail_sl_adjustment'],2)
                                            pegasus.log(f"trail sl after locked trail adjusted to {trail_sl} because current pnl is {pnl} for {timestamp}")
                                if (pnl < trail_sl) & (set_locked_trail_sl):
                                    cut_timestamp = timestamp
                                    cut_pnl_value = pnl
                                    note = "strategy_max_loss_hit"
                                    # print(f"trailing lock and trail sl got hit for the strategy @ {timestamp} @ {pnl}")
                                    pegasus.log(f"trailing lock and trail sl got hit for the strategy @ {timestamp} @ {pnl}")
                                    break
                                # this piece of code will take the overall target and overall sl into account and will exit the strategy when either of the condition is met
                                if strategy.overall_sl and pnl <= -strategy.overall_sl:
                                    cut_timestamp = timestamp
                                    cut_pnl_value = pnl
                                    # print(f"overall sl got hit for the strategy @ {timestamp} @ {pnl}")
                                    pegasus.log(f"overall sl got hit for the strategy @ {timestamp} @ {pnl}")
                                    note = "strategy_max_loss_hit"
                                    break
                                if strategy.overall_target  and pnl >= strategy.overall_target:
                                    cut_timestamp = timestamp
                                    cut_pnl_value = pnl
                                    # print(f"overall target got hit for the strategy @ {timestamp} @ {pnl}")
                                    pegasus.log(f"overall target got hit for the strategy @ {timestamp} @ {pnl}")
                                    note = "strategy_max_profit_hit"
                                    break
                    else:
                        # print("no trailing sl for the strategy, just processing the overall target and overall sl")
                        pegasus.log("no trailing sl for the strategy, just processing the overall target and overall sl")
                        for i, (timestamp, pnl) in enumerate(zip(pnl_df['timestamp'], pnl_df['pnl'])):
                            if max_profit is not False and pnl >= max_profit:
                                cut_timestamp = timestamp
                                cut_pnl_value = pnl
                                note = "strategy_max_profit_hit"
                                # print(f"overall target got hit for the strategy @ {timestamp} @ {pnl}")
                                pegasus.log(f"overall target got hit for the strategy @ {timestamp} @ {pnl}")
                                break
                            if max_loss is not False and pnl <= max_loss:
                                cut_timestamp = timestamp
                                cut_pnl_value = pnl
                                note = "strategy_max_loss_hit"
                                # print(f"overall sl got hit for the strategy @ {timestamp} @ {pnl}")
                                pegasus.log(f"overall sl got hit for the strategy @ {timestamp} @ {pnl}")
                                break
                        
                        if cut_timestamp is None:
                            break
            
                    if cut_timestamp is not None:
                        # print(f"cutting timestamp and saving the file for index {cut_timestamp}")
                        pegasus.log(f"cutting timestamp and saving the file for index {cut_timestamp}")
                        for file_name in os.listdir(item_path):
                            if file_name.endswith('.csv'):
                                file_path = os.path.join(item_path, file_name)
                                df = pd.read_csv(file_path)
                                cut_index = df[df['timestamp'] == cut_timestamp].index[0]
                                last_row = df.iloc[-1].copy()
                                cut_minutewise_pnl = df.loc[cut_index, 'pnl']
                                df.loc[cut_index:, 'pnl'] = cut_minutewise_pnl
                                df.loc[cut_index:, 'remark'] = note
                                df.to_csv(file_path, index=False)

                        if combined_pnl_file:
                            pnl_df.loc[cut_index + 1:, 'pnl'] = cut_pnl_value
                            pnl_df.to_csv(combined_pnl_file, index=False)
"""
    Retrieves the closest futures price (e.g., open or close) for a given index at or before a specified timestamp from a MySQL database.

    Parameters:
    - `index` (str): The index for which the futures price is needed.
    - `timestamp` (str or datetime): The target timestamp to find the closest price at or before.
    - `price_type` (str): The type of price to retrieve ('open', 'close', etc.).
    - `expiry` (str, optional): The contract expiry identifier (default is 'I').

    Workflow:
    - Converts the `timestamp` to a standard format.
    - Connects to the MySQL database and queries the relevant table for the specified `price_type`.
    - Orders results by timestamp in descending order to find the most recent price.
    - Returns the price if found, otherwise returns `None`.

    Returns:
    - The futures price at or before the given timestamp, or `None` if no data is found.
"""
def get_futures_price(index, timestamp, price_type, expiry='I'):
    timestamp = pd.to_datetime(timestamp)
    
    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    connection = mysql.connector.connect(
        host=db_config['host'],           
        user=db_config['user'],           
        password=db_config['password'],   
        database=db_config['database']    
    )
    
    cursor = connection.cursor(dictionary=True)
    
    table_name = f"{index}_fut"
    query = f"""
    SELECT {price_type}
    FROM {table_name}
    WHERE expiry = %s
    AND timestamp <= %s
    ORDER BY timestamp DESC
    LIMIT 1
    """
    cursor.execute(query, (expiry, timestamp_str))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if result:
        return result[price_type]
    else:
        return None
"""
    This function generates a combined report from multiple CSV files located in a specific folder associated with a given trading strategy.
    
    The function performs the following steps:
    
    1. **Folder Path Setup:**
        - The function determines the folder path using the `strategy.name` attribute, which corresponds to the directory containing the relevant CSV files for the strategy.

    2. **Reading CSV Files:**
        - The function iterates through all files in the specified folder.
        - For each file, it checks if the file is a valid CSV file (i.e., has a `.csv` extension and is not a subdirectory).
        - If a valid CSV file is found, it reads the contents of the file into a pandas DataFrame and appends this DataFrame to a list called `dataframes`.

    3. **Combining Data:**
        - If any DataFrames were collected during the previous step, the function concatenates all of them into a single DataFrame called `combined_df`.
        - The combined DataFrame is then sorted by the `entry_timestamp` column to ensure the trades are ordered chronologically.
        - The index of the combined DataFrame is reset to maintain a clean, sequential index.

    4. **Calculating Futures Prices:**
        - The function adds two new columns to the combined DataFrame: `entry_futures_price` and `exit_futures_price`.
        - These columns are calculated by applying a function (`get_futures_price`) to each row of the DataFrame.
        - The `get_futures_price` function retrieves the futures price at the specified `entry_timestamp` (using the 'open' price) and `exit_timestamp` (using the 'close' price) for the given `strategy.index`.

    5. **Output Generation:**
        - The function prints the combined DataFrame to the console for review.
        - It saves the combined DataFrame to a CSV file named `sample_response.csv`.
        - Finally, the combined data is converted to a JSON string in the `records` format, with dates formatted in ISO 8601 format, and this JSON string is returned as `server_response`.

    6. **No Data Condition:**
        - If no valid CSV files are found in the folder, the function returns `False`.
    """

def combined_report_generator(strategy, optimization_flag=False):
    folder_path = strategy.name
    dataframes = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.csv') and not file_name.startswith(folder_path):
            print(f"Processing file: {file_path}")
            df = pd.read_csv(file_path)
            dataframes.append(df)
    if dataframes:
        combined_df = pd.concat(dataframes)
        combined_df = combined_df.sort_values(by='entry_timestamp')
        combined_df.reset_index(drop=True, inplace=True)
        if optimization_flag == False:
            combined_df['entry_futures_price'] = combined_df.apply(
                lambda row: get_futures_price(strategy.index, row['entry_timestamp'], 'open'), axis=1)

            combined_df['exit_futures_price'] = combined_df.apply(
                lambda row: get_futures_price(strategy.index, row['exit_timestamp'], 'close'), axis=1)
        combined_df['max_profit']= round(combined_df["max_profit"],2)
        combined_df['max_loss']= round(combined_df["max_loss"],2)
        combined_df = update_tradebook_with_pnl(combined_df, strategy, 'trade_side')
        combined_df['pnl']= round(combined_df["pnl"],2)
        combined_df['sl'].apply(round_to_tick)
        # print(combined_df.columns)
        file_path = os.path.join(strategy.name, f'{os.path.basename(strategy.name)}_combined_tradebook.csv')
        combined_df.to_csv(file_path, index=False)
        # combined_df.to_csv("test.csv", index=False)
        # print(combined_df)
        # overall_performance = analyze_tradebook(combined_df)
        
        # return overall_performance #server_response
    # else:
    #     return False



def get_last_expiry(dates):
    last_expiry = defaultdict(lambda: date.min)
    for d in dates:
        if d > last_expiry[d.month]:
            last_expiry[d.month] = d
    return [last_expiry[month] for month in sorted(last_expiry)]

def find_keys_by_value(d, target_value):
    keys = [key for key, value in d.items() if value == target_value]
    return keys


"""
This function parse dates from string to datetime format
"""
def parse_date(date_str):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        print('error occured')




def parse_roll_strike(roll_strike_criteria, option_type, current_atm, base=100):
    match = re.match(r'^(atm|otm|itm)(\d*)$', roll_strike_criteria.lower())
    if match:
        strike_type, number = match.groups()
        number = int(number) if number else 0
        # print(f"Strike type: {strike_type}, Number: {number}")
        if strike_type == 'atm':
            return current_atm
        elif strike_type == 'otm':
            if option_type.lower() =='ce':
                return current_atm + number * base
            else:
                return current_atm - number * base
        elif strike_type == 'itm':
            if option_type.lower() =='ce':
                return current_atm - number * base
            else:
                return current_atm + number * base
    return None
def drawdown_analyzer(drawdown_path):
    df = pd.read_csv(drawdown_path)
    df['strategy_date'] = pd.to_datetime(df['strategy_date'])
    system_drawdown_start, system_drawdown_end, system_drawdown, system_drawdown_duration = calculate_drawdown(df)
    yearly_drawdowns ={}
    df['year'] = df['strategy_date'].dt.year
    years = df['year'].unique()
    for year in years:
        df_year = df[df['year'] == year]
        if not df_year.empty:
            drawdown_start, drawdown_end, drawdown, drawdown_duration = calculate_drawdown(df_year)
            yearly_drawdowns[str(year)] = {
                'max_drawdown': drawdown,
                'drawdown_start': drawdown_start,
                'drawdown_end': drawdown_end,
                'max_drawdown_duration': str(drawdown_duration)
            }
    return system_drawdown_start, system_drawdown_end, system_drawdown, system_drawdown_duration, yearly_drawdowns
    # df = df[['strategy_date', 'mtm']]
    # df['strategy_date'] = pd.to_datetime(df['strategy_date'])
    # df['mtm'] = df['mtm'].cumsum()
    # df['max_data_mtm'] = df['mtm'].cummax()
    # df['drawdown'] = df['mtm'] - df['max_data_mtm']

    # # Initialize variables for system drawdown
    # drawdown_periods = []
    # drawdown_dates = []
    # drawdown_amounts = []
    # in_drawdown = False
    # min_drawdown = 0

    # for idx, row in df.iterrows():
    #     if row['drawdown'] < 0:
    #         if not in_drawdown:
    #             in_drawdown = True
    #             drawdown_start_idx = idx
    #             drawdown_start_date = row['strategy_date']
    #             min_drawdown = row['drawdown']
    #         else:
    #             min_drawdown = min(min_drawdown, row['drawdown'])
    #     else:
    #         if in_drawdown:
    #             in_drawdown = False
    #             drawdown_end_idx = idx
    #             drawdown_end_date = row['strategy_date']
    #             drawdown_duration = drawdown_end_idx - drawdown_start_idx
    #             drawdown_periods.append(drawdown_duration)
    #             drawdown_dates.append((drawdown_start_date.date(), drawdown_end_date.date()))
    #             drawdown_amounts.append(abs(min_drawdown))

    # # Handle case where drawdown is ongoing at the end of data
    # if in_drawdown:
    #     drawdown_end_idx = df.index[-1]
    #     drawdown_end_date = df.iloc[-1]['strategy_date']
    #     drawdown_duration = drawdown_end_idx - drawdown_start_idx
    #     drawdown_periods.append(drawdown_duration)
    #     drawdown_dates.append((drawdown_start_date.date(), drawdown_end_date.date()))
    #     drawdown_amounts.append(abs(min_drawdown))

    # if drawdown_periods:
    #     system_drawdown_duration = max(drawdown_periods)
    #     max_drawdown_period_index = drawdown_periods.index(system_drawdown_duration)
    #     system_drawdown_start, system_drawdown_end = drawdown_dates[max_drawdown_period_index]
    #     system_drawdown = round(max(drawdown_amounts), 2)
    # else:
    #     system_drawdown_duration = 0
    #     system_drawdown_start, system_drawdown_end, system_drawdown = None, None, 0

    # # Now compute the yearly drawdowns
    # yearly_drawdowns = {}
    # df['year'] = df['strategy_date'].dt.year
    # years = df['year'].unique()

    # for year in years:
    #     df_year = df[df['year'] == year]
    #     if not df_year.empty:
    #         min_drawdown_value = df_year['drawdown'].min()
    #         min_drawdown = abs(min_drawdown_value)
    #         min_drawdown_idx = df_year['drawdown'].idxmin()

    #         # Get the corresponding drawdown start and end dates
    #         df_up_to_min = df.loc[:min_drawdown_idx]
    #         df_up_to_min_zero = df_up_to_min[df_up_to_min['drawdown'] == 0]

    #         if not df_up_to_min_zero.empty:
    #             drawdown_start_idx = df_up_to_min_zero.index[-1]
    #             drawdown_start_date = df.loc[drawdown_start_idx, 'strategy_date']
    #         else:
    #             drawdown_start_date = df.iloc[0]['strategy_date']

    #         df_from_min = df.loc[min_drawdown_idx:]
    #         df_from_min_zero = df_from_min[df_from_min['drawdown'] == 0]

    #         if not df_from_min_zero.empty:
    #             drawdown_end_idx = df_from_min_zero.index[0]
    #             drawdown_end_date = df.loc[drawdown_end_idx, 'strategy_date']
    #         else:
    #             drawdown_end_date = df.iloc[-1]['strategy_date']

    #         # Find the difference in index between drawdown_start and drawdown_end
    #         drawdown_start_idx = df[df['strategy_date'] == drawdown_start_date].index[0]
    #         drawdown_end_idx = df[df['strategy_date'] == drawdown_end_date].index[0]
    #         max_drawdown_duration = drawdown_end_idx - drawdown_start_idx

    #         yearly_drawdowns[str(year)] = {
    #             'max_drawdown': min_drawdown,
    #             'drawdown_start': drawdown_start_date+ timedelta(days=1),
    #             'drawdown_end': drawdown_end_date,
    #             'max_drawdown_duration': str(max_drawdown_duration-1)
    #         }
    # print(yearly_drawdowns)
    # return system_drawdown_start, system_drawdown_end, system_drawdown, system_drawdown_duration, yearly_drawdowns


def calculate_drawdown(data):  
    df = data.copy()
    df = df[['strategy_date', 'mtm']]
    df['strategy_date'] = pd.to_datetime(df['strategy_date'])
    df['mtm'] = df['mtm'].cumsum()
    df['max_data_mtm'] = df['mtm'].cummax()
    df['drawdown'] = df['mtm'] - df['max_data_mtm']
    print(df)
    drawdown_periods = []
    drawdown_dates = []
    drawdown_amounts = []
    in_drawdown = False
    min_drawdown = 0

    for idx, row in df.iterrows():
        if row['drawdown'] < 0:
            if not in_drawdown:
                in_drawdown = True
                drawdown_start_idx = idx
                drawdown_start_date = row['strategy_date']
                min_drawdown = row['drawdown']
            else:
                min_drawdown = min(min_drawdown, row['drawdown'])
        else:
            if in_drawdown:
                in_drawdown = False
                drawdown_end_idx = idx
                drawdown_end_date = row['strategy_date']
                drawdown_duration = drawdown_end_idx - drawdown_start_idx
                drawdown_periods.append(drawdown_duration)
                drawdown_dates.append((drawdown_start_date.date(), drawdown_end_date.date()))
                drawdown_amounts.append(abs(min_drawdown))

    if in_drawdown:
        drawdown_end_idx = df.index[-1]
        drawdown_end_date = df.iloc[-1]['strategy_date']
        drawdown_duration = drawdown_end_idx - drawdown_start_idx
        drawdown_periods.append(drawdown_duration)
        drawdown_dates.append((drawdown_start_date.date(), drawdown_end_date.date()))
        drawdown_amounts.append(abs(min_drawdown))

    if drawdown_periods:
        system_drawdown_duration = max(drawdown_periods)
        max_drawdown_period_index = drawdown_periods.index(system_drawdown_duration)
        system_drawdown_start, system_drawdown_end = drawdown_dates[max_drawdown_period_index]
        system_drawdown = round(max(drawdown_amounts), 2)
    else:
        system_drawdown_duration = 0
        system_drawdown_start, system_drawdown_end, system_drawdown = None, None, 0
    print(system_drawdown_start, system_drawdown_end, system_drawdown, system_drawdown_duration)
    return system_drawdown_start, system_drawdown_end, system_drawdown, system_drawdown_duration




def analyze_tradebook(strategy):
    df = pd.read_csv(os.path.join(strategy.name, f"{strategy.name}_combined_tradebook.csv"))
    drawdown_path = os.path.join(strategy.name, f"{strategy.name}_strategy_pnl_details.csv")
    df['entry_date'] = pd.to_datetime(df['entry_time']).dt.date
    daily_pnl = df.groupby('entry_date')['pnl'].sum().to_dict()
    total_pnl = round(sum(daily_pnl.values()),2)
    total_days = len(daily_pnl)
    winning_days = sum(1 for pnl in daily_pnl.values() if pnl > 0)
    losing_days = sum(1 for pnl in daily_pnl.values() if pnl < 0)
    average_profit_per_day = sum(pnl for pnl in daily_pnl.values())/total_days
    average_profit_on_winning_days = sum(pnl for pnl in daily_pnl.values() if pnl > 0) / winning_days if winning_days > 0 else 0
    OverallProfit = round((sum(pnl for pnl in daily_pnl.values() if pnl > 0)),2)
    OverallLoss = round((sum(pnl for pnl in daily_pnl.values() if pnl < 0)),2)
    average_loss_on_losing_days = sum(pnl for pnl in daily_pnl.values() if pnl < 0) / losing_days if losing_days > 0 else 0
    max_loss_single_day = min(daily_pnl.values())
    max_profit_single_day = max(daily_pnl.values())
    winning_percentage = (winning_days / total_days) * 100 if total_days > 0 else 0
    losing_percentage = (losing_days / total_days) * 100 if total_days > 0 else 0
    drawdown_start_date, drawdown_end_date, max_drawdown, max_drawdown_duration, yearly_drawdowns = drawdown_analyzer(drawdown_path)
    print(f"yearly drawdown is {yearly_drawdowns}")
    #changed this part to handle divided by zero error
    try:
        RiskToRewardRatio = abs(average_profit_on_winning_days/average_loss_on_losing_days)
    except Exception as e:
        RiskToRewardRatio = 0
    ExpectancyRatio = round((RiskToRewardRatio*winning_percentage - losing_percentage)/100,2)
    streak = 0
    max_winning_streak = 0
    max_losing_streak = 0
    current_streak_type = None  

    for pnl in daily_pnl.values():
        if pnl > 0:  
            if current_streak_type == 'losing':
                streak = 0  
            streak += 1
            max_winning_streak = max(max_winning_streak, streak)
            current_streak_type = 'winning'
        elif pnl < 0:  
            if current_streak_type == 'winning':
                streak = 0  
            streak += 1
            max_losing_streak = max(max_losing_streak, streak)
            current_streak_type = 'losing'
        else:
            streak = 0  
    tradebook_copy = df.copy()
    tradebook_copy['Charges'] = tradebook_copy.apply(apply_charges, axis=1)

    # Extracting brokerage and other charges from the calculated dictionary
    tradebook_copy['Brokerage'] = tradebook_copy['Charges'].apply(lambda x: x['brokerage'])
    tradebook_copy['OtherCharges'] = tradebook_copy['Charges'].apply(lambda x: x['otherCharges'])
    tradebook_copy.to_csv('starx.csv', index=False)
    # Calculate total brokerage and total other charges
    total_brokerage_sum = tradebook_copy['Brokerage'].sum()
    total_other_charges_sum = tradebook_copy['OtherCharges'].sum()
    print(total_brokerage_sum, total_other_charges_sum, "is brokerage and tax")


    OverallPerformance ={
        "TotalProfit": total_pnl,
        "NetProfit": round(total_pnl - float(total_brokerage_sum + total_other_charges_sum), 2),
        "OverallLoss": OverallLoss,
        "OverallProfit": OverallProfit,
        "DaysProfit": winning_days,
        "DaysLoss": losing_days,
        "TotalTradingDays": total_days,
        "AverageProfit" : round(average_profit_on_winning_days,2),
        "AverageLoss": round(average_loss_on_losing_days,2),
        "RiskToRewardRatio": round(RiskToRewardRatio,2),
        "MaxProfitInSingleTrade": max_profit_single_day,
        "MaxLossInSingleTrade" : max_loss_single_day,
        "MaxDrawdown" : max_drawdown,
        "DurationOfMaxDrawdown" : {"days": max_drawdown_duration,
                                   "start":drawdown_start_date,
                                   "end": drawdown_end_date
                                    },
        "MaxDDPeriod": max_drawdown_duration, #static for now
        "ExpectancyRatio" : ExpectancyRatio,
        "MaxWinningStreak": max_winning_streak,
        "MaxLosingStreak": max_losing_streak,
        "TaxAndCharges": {
            "Brokerage": str(total_brokerage_sum),
            "OtherCharges": str(total_other_charges_sum),
            "totalCharges" : str(total_brokerage_sum + total_other_charges_sum),
        },
        "yearlyDrawdowns": yearly_drawdowns

    }
    print(f"OverAll Performance is {OverallPerformance}")
    return OverallPerformance





def analyse_legs_pnl(root_dir):
    combined_data = []

    for folder_name in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder_name)
        if os.path.isdir(folder_path):
            daily_pnl = pd.DataFrame()  # Empty DataFrame for each folder (strategy date)
            
            # Iterate over files in the folder
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.csv') and '_minutewise_' in file_name:
                    file_path = os.path.join(folder_path, file_name)
                    df = pd.read_csv(file_path)  # Read CSV file

                    if daily_pnl.empty:
                        daily_pnl = df[['timestamp', 'pnl']]  # Initialize with first CSV's pnl
                    else:
                        # Merge with new pnl data
                        daily_pnl = pd.merge(daily_pnl, df[['timestamp', 'pnl']], on='timestamp', how='outer')
                        # Sum all pnl columns and store in 'pnl'
                        daily_pnl['pnl'] = daily_pnl.filter(like='pnl').sum(axis=1)
                        # Drop the extra pnl columns
                        daily_pnl = daily_pnl[['timestamp', 'pnl']]

            if not daily_pnl.empty:
                max_profit = daily_pnl['pnl'].max()
                max_loss = daily_pnl['pnl'].min()
                max_profit_time = daily_pnl.loc[daily_pnl['pnl'] == max_profit, 'timestamp'].values[0]
                max_loss_time = daily_pnl.loc[daily_pnl['pnl'] == max_loss, 'timestamp'].values[0]
                mtm = daily_pnl['pnl'].iloc[-1]

                # Store the result in the list instead of appending to the DataFrame
                combined_data.append({
                    'strategy_date': folder_name,
                    'max_profit': max_profit,
                    'max_loss': max_loss,
                    'max_profit_timestamp': max_profit_time,
                    'max_loss_timestamp': max_loss_time,
                    'mtm': mtm
                })

    # Convert the list of dicts to a DataFrame at the end
    combined_df = pd.DataFrame(combined_data)
    
    return combined_df

def analyse_combined_strategy(root_dir):
    print("inside analyse_combined_strategy")
    combined_df = analyse_legs_pnl(root_dir)
    combined_df.sort_values(by=['strategy_date'], inplace=True)
    combined_df['max_profit'] = round(combined_df['max_profit'], 2)
    combined_df['max_loss'] = round(combined_df['max_loss'], 2)
    combined_df['mtm'] = round(combined_df['mtm'], 2)
    combined_df.sort_values('strategy_date', inplace=True)
    output_file_path = os.path.join(root_dir, f'{os.path.basename(root_dir)}_strategy_pnl_details.csv')
    combined_df.to_csv(output_file_path, index=False)
    print(combined_df)






def convert_dates_to_string(data):
    if isinstance(data, dict):
        return {k: convert_dates_to_string(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_dates_to_string(item) for item in data]
    elif isinstance(data, dt.date):
        return data.strftime("%Y-%m-%d")  # Convert to 'YYYY-MM-DD' string
    return data


def update_tradebook_with_strategy_pnl(strategy, optimization_flag=False):
    folder_path = strategy.name
    tradebook_df = pd.read_csv(os.path.join(folder_path, f'{strategy.name}_combined_tradebook.csv'))
    strategy_pnl_df = pd.read_csv(os.path.join(folder_path, f'{strategy.name}_strategy_pnl_details.csv'))    
    tradebook_df['entry_timestamp'] = pd.to_datetime(tradebook_df['entry_timestamp'])
    strategy_pnl_df['strategy_date'] = pd.to_datetime(strategy_pnl_df['strategy_date'])
    tradebook_df['MaxProfitStrategy'] = None
    tradebook_df['MaxLossStrategy'] = None
    for index, row in strategy_pnl_df.iterrows():
        matching_rows = tradebook_df[tradebook_df['entry_timestamp'].dt.date == row['strategy_date'].date()]
        
        if not matching_rows.empty:
            max_profit_timestamp = datetime.strptime(row['max_profit_timestamp'], '%Y-%m-%d %H:%M:%S')
            max_loss_timestamp = datetime.strptime(row['max_loss_timestamp'], '%Y-%m-%d %H:%M:%S')
            max_profit_str = f"{row['max_profit']} @ {max_profit_timestamp.time()}"
            max_loss_str = f"{row['max_loss']} @ {max_loss_timestamp.time()}"            
            first_match_idx = matching_rows.index[0]
            tradebook_df.at[first_match_idx, 'MaxProfitStrategy'] = max_profit_str
            tradebook_df.at[first_match_idx, 'MaxLossStrategy'] = max_loss_str
    if not optimization_flag:
        tradebook_df.rename(columns={
            'symbol': 'symbol',
            'entry_timestamp': 'entry_time',
            'entry_price': 'entry_price',
            'exit_timestamp': 'exit_time',
            'exit_price': 'exit_price',
            'sl': 'sl',
            'tsl': 'tsl',
            'quantity': 'qty',
            'pnl': 'pnl',
            'MaxLossStrategy': 'maxLossStrategy',
            'MaxProfitStrategy': 'maxProfitStrategy',
            'entry_futures_price': 'futureEntry',
            'exit_futures_price': 'futureExit',
            'remark': 'comment',
            'trade_side': 'trade'
        }, inplace=True)

        columns_order = [
            'symbol', 'trade', 'entry_time', 'entry_price', 'exit_time', 'exit_price', 
            'sl', 'tsl', 'qty', 'pnl', 'maxLossStrategy', 'maxProfitStrategy', 
            'futureEntry', 'futureExit', 'comment'
        ]
    else:
        tradebook_df.rename(columns={
            'symbol': 'symbol',
            'entry_timestamp': 'entry_time',
            'entry_price': 'entry_price',
            'exit_timestamp': 'exit_time',
            'exit_price': 'exit_price',
            'sl': 'sl',
            'tsl': 'tsl',
            'quantity': 'qty',
            'pnl': 'pnl',
            'MaxLossStrategy': 'maxLossStrategy',
            'MaxProfitStrategy': 'maxProfitStrategy',
            'remark': 'comment',
            'trade_side': 'trade'
        }, inplace=True)

        columns_order = [
            'symbol', 'trade', 'entry_time', 'entry_price', 'exit_time', 'exit_price', 
            'sl', 'tsl', 'qty', 'pnl', 'maxLossStrategy', 'maxProfitStrategy', 
             'comment'
        ]

    tradebook_df = tradebook_df[columns_order]
    tradebook_df.to_csv(os.path.join(folder_path, f'{strategy.name}_combined_tradebook.csv'))

    return tradebook_df



def convert_numpy_types(data: Any) -> Any:
    """
    Recursively convert numpy types to native Python types.
    """
    if isinstance(data, dict):
        return {key: convert_numpy_types(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    elif isinstance(data, np.generic):  # Handles numpy types like int64, float64, etc.
        return data.item()
    else:
        return data
    


