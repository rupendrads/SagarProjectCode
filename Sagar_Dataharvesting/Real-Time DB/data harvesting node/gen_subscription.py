import subprocess
import sys
import requests
import os
import zipfile
import pandas as pd
import json
from datetime import datetime, timedelta
from broker import XTSlogin


def download_zip_file(url, filename):
    try:
        # Get the current directory
        current_directory = os.getcwd()
        
        # Complete file path
        output_path = os.path.join(current_directory, filename)
        
        # Headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.nseindia.com/",
        }
        
        # Send the GET request
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes

        # Write the content to the file
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"File downloaded successfully and saved to: {output_path}")
        return output_path  # Return the file path for extraction
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

def extract_zip_file(zip_path, extract_to=None):
    try:
        # Set the extraction path to the current directory if not specified
        if extract_to is None:
            extract_to = os.getcwd()

        # Open the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all the contents
            zip_ref.extractall(extract_to)
            print(f"Contents extracted to: {extract_to}")
    except zipfile.BadZipFile:
        print(f"Error: {zip_path} is not a valid zip file.")
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_zip_file(zip_path):
    try:
        # Delete the zip file after extraction
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print(f"ZIP file {zip_path} deleted successfully.")
        else:
            print(f"ZIP file {zip_path} does not exist.")
    except Exception as e:
        print(f"Error deleting zip file: {e}")

def get_last_thursday_of_month(year, month):
    """Find the last Thursday of a given month."""
    # Get the last day of the month
    last_day = datetime(year, month + 1, 1) - timedelta(days=1) if month < 12 else datetime(year + 1, 1, 1) - timedelta(days=1)
    
    # Find the last Thursday
    while last_day.weekday() != 3:  # 3 corresponds to Thursday
        last_day -= timedelta(days=1)
    return last_day

def rename_extracted_files(extract_to):
    try:
        # Loop through the extracted files
        for file_name in os.listdir(extract_to):
            #print(file_name)
            #print(extract_to)
            file_path = os.path.join(extract_to, file_name)

            # Only process .csv files
            if file_name.endswith(".csv"):
                # Check if the file name starts with 'fo' or 'op' and ends with a date-like suffix
                if file_name.startswith("fo"):  # Expected format: fo031224.csv
                    print(file_name)
                    new_name = os.path.join(extract_to, "fo.csv")
                    os.rename(file_path, new_name)
                    print(f"File renamed to: {new_name}")

                elif file_name.startswith("op"):  # Expected format: op031224.csv
                    print(file_name)
                    new_name = os.path.join(extract_to, "op.csv")
                    os.rename(file_path, new_name)
                    print(f"File renamed to: {new_name}")
    except Exception as e:
        print(f"Error renaming files: {e}")

def generate_nfo():
    # Paths to the CSV files
    nfo_csv_path = 'nfo.csv'
    bfo_csv_path = 'bfo.csv'

    # Check if the CSV files exist and delete them
    if os.path.exists(nfo_csv_path):
        os.remove(nfo_csv_path)
        print(f"{nfo_csv_path} has been deleted.")
    else:
        print(f"Error: {nfo_csv_path} does not exist.")

    if os.path.exists(bfo_csv_path):
        os.remove(bfo_csv_path)
        print(f"{bfo_csv_path} has been deleted.")
    else:
        print(f"Error: {bfo_csv_path} does not exist.")

    # Path to your JavaScript file
    js_file_path = 'nfo_generator.js'

    # Run the JavaScript file using Node.js
    try:
        result = subprocess.run(['node', js_file_path], check=True, text=True, capture_output=True)
        print("JavaScript output:", result.stdout)  # Output from the JS file
    except subprocess.CalledProcessError as e:
        print("Error running JavaScript file:", e)
        print("Error output:", e.stderr)

def generate_bhavcopy():
    fo_path = 'fo.csv'
    op_path = 'op.csv'

    # Check if the CSV files exist and delete them
    if os.path.exists(fo_path):
        os.remove(fo_path)
        print(f"{fo_path} has been deleted.")
    else:
        print(f"Error: {fo_path} does not exist.")

    if os.path.exists(op_path):
        os.remove(op_path)
        print(f"{op_path} has been deleted.")
    else:
        print(f"Error: {op_path} does not exist.")

    url = "https://nsearchives.nseindia.com/content/fo/fo.zip"
    # File name to save in the current directory
    filename = "fo.zip"
    # Download the zip file
    zip_path = download_zip_file(url, filename)
    # Extract the zip file if the download was successful
    if zip_path:
        extract_zip_file(zip_path)
        # Rename the extracted files
        #print(os.getcwd())
        rename_extracted_files(os.getcwd())
        # Delete the zip file after extraction and renaming
        delete_zip_file(zip_path)

def get_nfo_futures_data():
    lists = ['NIFTY 50', 'NIFTY MID SELECT', 'NIFTY FIN SERVICE', 'NIFTY BANK']
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv('nfo.csv',low_memory=False)

    # Convert the 'UnderlyingIndexName' column to uppercase for all row
    # Initialize the list to store the final results
    result_list = []


    for value in lists:
        df['UnderlyingIndexName'] = df['UnderlyingIndexName'].str.upper()
        # Filter the DataFrame for 'FUTIDX' and the current 'UnderlyingIndexName'
        filtered_df = df[(df['Series'] == 'FUTIDX') & (df['UnderlyingIndexName'] == value)]
        #print(filtered_df)
        # Select the top 2 rows
        sorted_rows = filtered_df.sort_values(by='ContractExpiration')
        #print(sorted_rows)
        top_2_rows = sorted_rows.head(2)

        
        # Extract the InstrumentID and InstrumentType for the top 2 rows
        result = top_2_rows[['ExchangeInstrumentID', 'InstrumentType']]

        # Convert the result to a list of dictionaries
        result_dict = result.to_dict(orient='records')

        for entry in result_dict:
            entry['exchangeInstrumentID'] = entry.pop('ExchangeInstrumentID')
            entry['exchangeSegment'] = entry.pop('InstrumentType')

        # Append the result to the result_list
        result_list.extend(result_dict)

    return result_list

def get_bfo_futures_data():
    lists = ['BANKEX', 'SENSEX']
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv('bfo.csv',low_memory=False)

    # Convert the 'UnderlyingIndexName' column to uppercase for all row
    # Initialize the list to store the final results
    result_list = []


    for value in lists:
        df['UnderlyingIndexName'] = df['UnderlyingIndexName'].str.upper()
        # Filter the DataFrame for 'FUTIDX' and the current 'UnderlyingIndexName'
        filtered_df = df[(df['Series'] == 'IF') & (df['UnderlyingIndexName'] == value)]
        #print(filtered_df)
        # Select the top 2 rows
        sorted_rows = filtered_df.sort_values(by='ContractExpiration')
        #print(sorted_rows)
        top_2_rows = sorted_rows.head(2)

        
        # Extract the InstrumentID and InstrumentType for the top 2 rows
        result = top_2_rows[['ExchangeInstrumentID', 'InstrumentType']]

        # Convert the result to a list of dictionaries
        result_dict = result.to_dict(orient='records')

        for entry in result_dict:
            entry['exchangeInstrumentID'] = entry.pop('ExchangeInstrumentID')
            entry['exchangeSegment'] = entry.pop('InstrumentType')

        # Append the result to the result_list
        result_list.extend(result_dict)

    return result_list



def get_nfo_op_data():
    lists = ['NIFTY 50', 'NIFTY BANK', 'NIFTY FIN SERVICE', 'NIFTY MID SELECT']
    #lists = ['NIFTY 50']
    #root_url = "https://ttblaze.iifl.com/"
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv('nfo.csv', low_memory=False)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_dir, '..', '..', '..', 'Sagar_Common', 'config_dev.json')
    with open(config_file_path, "r") as file:
        config = json.load(file)
    # Extract the port URL
    root_url = config["live_creds"]["port"]
    print(f"Root URL: {root_url}")
    # Initialize the list to store the final results
    result_list = []
    range_value = config["strike_range"]["range"]
    with open('nfoconfig.json', 'r') as config_file:
        config = json.load(config_file)

    for value in lists:
        instrument = []
        xts = XTSlogin(root_url)
        with open('secret.json', 'r') as file:
            credentials = json.load(file)
            app_key = credentials.get("app_key")
            secret_key = credentials.get("secret_key")

            if not app_key or not secret_key:
                print("Error: Missing app_key or secret_key in the file.")

        token, userid = xts.market_login(secret_key,app_key)
        print(token)
        instrument.append(value)
        print(instrument, token)
        #strike_value = xts.get_quotes(instrument,token)
        strike_value = 34650
        strike_value = (
            34650 if value == 'NIFTY 50' else
            53600 if value == 'NIFTY BANK' else
            13000 if value == 'NIFTY MID SELECT' else
            24900
        )


        print("STRIKE VALUE")
        print(strike_value)
        percent_range = (strike_value * (range_value/100))

        expiry_str = config[value]["expiry"]
        existing_strike_value = config[value]['instrument_price']
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
        today = "2024-12-27"
        today_date = datetime.strptime(today, "%Y-%m-%d").date()
        if today_date > expiry_date.date():
            print(f"{value} expired, resetting values.")
            config[value]["min_value"] = float('inf')
            config[value]["max_value"] = float('-inf')
            config[value]["expiry"] = (datetime.now().replace(day=1).date()).strftime("%Y-%m-%d")
            config[value]['instrument_price'] = strike_value

        if existing_strike_value != None:
            if strike_value > existing_strike_value:
            # Calculate the min and max range
                min_range = config[value]["min_value"]
                max_range = int(strike_value + percent_range)
                config[value]["max_value"] = max_range
                config[value]["instrument_price"] = strike_value
                print(min_range)
                print(max_range)
            
            elif strike_value < existing_strike_value:
                min_range = int(strike_value - percent_range)
                max_range = config[value]["max_value"]
                config[value]["min_value"] = min_range
                config[value]["instrument_price"] = strike_value
                print(min_range)
                print(max_range)
            
            else:
                min_range = int(strike_value - percent_range)
                max_range = int(strike_value + percent_range)
                print(min_range)
                print(max_range)
                config[value]["min_value"] = min_range
                config[value]["max_value"] = max_range
                config[value]["instrument_price"] = strike_value
        else:
            min_range = int(strike_value - percent_range)
            max_range = int(strike_value + percent_range)
            print(min_range)
            print(max_range)
            config[value]["min_value"] = min_range
            config[value]["max_value"] = max_range
            config[value]["instrument_price"] = strike_value

        # Write to config.json
        with open('nfoconfig.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)

        print("Min and Max ranges saved to config.json")

        df['UnderlyingIndexName'] = df['UnderlyingIndexName'].str.upper()

        df['ContractExpiration'] = pd.to_datetime(df['ContractExpiration']).dt.date

        # Filter the DataFrame for 'OPTIDX' and the current 'UnderlyingIndexName'
        filtered_df = df[(df['Series'] == 'OPTIDX') & (df['UnderlyingIndexName'] == value)]
        all_descriptions = filtered_df['DisplayName'].drop_duplicates().tolist()

        #print(all_descriptions)
        #print("filtered_df")
        #print(filtered_df)
        # Get unique StrikePrices (as strings)

        unique_strikes = filtered_df['StrikePrice'].drop_duplicates().tolist()
        #print(unique_strikes)
        filtered_strikes = [strike for strike in unique_strikes if min_range <= float(strike) <= max_range]

        # Print the filtered strikes
        #print("Filtered Strikes within range:", filtered_strikes)
        # Iterate over unique strike prices
        for strike in filtered_strikes:
            
                # Filter for OptionType = 3 (CE) for each StrikePrice
            ce_option_data = filtered_df[
                ((filtered_df['StrikePrice'] == strike) &
                (filtered_df['OptionType'] == 3))]

            pe_option_data = filtered_df[
                ((filtered_df['StrikePrice'] == strike) &
                (filtered_df['OptionType'] == 4))]
                    # Sort by ContractExpiration (to ensure chronological order)
            sorted_ce_data = ce_option_data.sort_values(by='ContractExpiration')
            sorted_pe_data = pe_option_data.sort_values(by='ContractExpiration')
                
            #print(sorted_ce_data)
            #print(sorted_pe_data)
                # Ensure there are enough rows before selecting them

            if value != "NIFTY 50":
                # Select top 2 rows for CE and PE
                top_2_ce_rows = sorted_ce_data.head(2)
                top_2_pe_rows = sorted_pe_data.head(2)

                # Append top 2 CE rows
                for df_subset in [top_2_ce_rows]:
                    result = df_subset[['ExchangeInstrumentID', 'InstrumentType']]
                    result_df = pd.DataFrame(result)
                    result_dict = result_df.to_dict(orient='records')
                    #print(result_dict)
                    for entry in result_dict:
                        if 'ExchangeInstrumentID' in entry:
                            entry['exchangeInstrumentID'] = entry.pop('ExchangeInstrumentID', None)
                        if 'InstrumentType' in entry:
                            entry['exchangeSegment'] = entry.pop('InstrumentType', None)
                    result_list.extend(result_dict)

                # Append top 2 PE rows
                for df_subset in [top_2_pe_rows]: 
                    result = df_subset[['ExchangeInstrumentID', 'InstrumentType']]
                    result_df = pd.DataFrame(result)
                    result_dict = result_df.to_dict(orient='records')
                    #print(result_dict)
                    for entry in result_dict:
                        if 'ExchangeInstrumentID' in entry:
                            entry['exchangeInstrumentID'] = entry.pop('ExchangeInstrumentID', None)
                        if 'InstrumentType' in entry:
                            entry['exchangeSegment'] = entry.pop('InstrumentType', None)
                    result_list.extend(result_dict)   
                
            
            else:
                current_ce_week_exp = sorted_ce_data.iloc[[0]]
                next_ce_week_exp = sorted_ce_data.iloc[[1]]
                current_ce_month_exp = sorted_ce_data.iloc[[2]]
                next_ce_month_exp = sorted_ce_data.iloc[[3]]

                current_pe_week_exp = sorted_pe_data.iloc[[0]]
                next_pe_week_exp = sorted_pe_data.iloc[[1]]
                current_pe_month_exp = sorted_pe_data.iloc[[2]]
                next_pe_month_exp = sorted_pe_data.iloc[[3]]

                
                for df_subset, label in [
                    (current_ce_week_exp, "current_ce_week_exp"),
                    (next_ce_week_exp, "next_ce_week_exp"),
                    (current_ce_month_exp, "current_ce_month_exp"),
                    (next_ce_month_exp, "next_ce_month_exp"),
                    (current_pe_week_exp, "current_pe_week_exp"),
                    (next_pe_week_exp, "next_pe_week_exp"),
                    (current_pe_month_exp, "current_pe_month_exp"),
                    (next_pe_month_exp, "next_pe_month_exp")
                ]:
                    # Select specific columns
                    result = df_subset[['ExchangeInstrumentID', 'InstrumentType']]

                    # Convert the result (Series) to a DataFrame and then to a list of dictionaries
                    result_df = pd.DataFrame(result)  # Convert to DataFrame
                    result_dict = result_df.to_dict(orient='records')  # Convert DataFrame to list of dicts
                    
                    # Debug: Print the result_dict to inspect the structure
                    #print(result_dict)

                    # Rename keys and ensure correct structure
                    for entry in result_dict:
                        if 'ExchangeInstrumentID' in entry:  # Check if the key exists
                            entry['exchangeInstrumentID'] = entry.pop('ExchangeInstrumentID', None)
                        if 'InstrumentType' in entry:  # Check if the key exists
                            entry['exchangeSegment'] = entry.pop('InstrumentType', None)

                            # Append to the final result list
                    result_list.extend(result_dict)
            
        '''
        liquid_data = get_nfo_liquid_strikes(all_descriptions) 
        print("LIQUID VALUES ARE")
        #print(liquid_data)
        #print(liquid_data)
        for data in liquid_data:
            liquid_data_row = df[df['DisplayName'] == data]
            print(liquid_data_row)
    
            if not liquid_data_row.empty:
                
                result = liquid_data_row[['ExchangeInstrumentID', 'InstrumentType']]

                    # Convert the result (Series) to a DataFrame and then to a list of dictionaries
                result_df = pd.DataFrame(result)  # Convert to DataFrame
                result_dict = result_df.to_dict(orient='records')  # Convert DataFrame to list of dicts
                #print(result_dict)
                for entry in result_dict:
                    if 'ExchangeInstrumentID' in entry:  # Check if the key exists
                        entry['exchangeInstrumentID'] = entry.pop('ExchangeInstrumentID', None)
                    if 'InstrumentType' in entry:  # Check if the key exists
                        entry['exchangeSegment'] = entry.pop('InstrumentType', None)

                            # Append to the final result list
                result_list.extend(result_dict)
            '''

    return result_list


def get_bfo_op_data():
    lists = ['BANKEX', 'SENSEX']
    #root_url = "https://ttblaze.iifl.com/"
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv('bfo.csv', low_memory=False)
    # Initialize the list to store the final results
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_dir, '..', '..', '..', 'Sagar_Common', 'config_dev.json')
    with open(config_file_path, "r") as file:
        config = json.load(file)
    # Extract the port URL
    root_url = config["live_creds"]["port"]
    print(f"Root URL: {root_url}")
    # Initialize the list to store the final results
    result_list = []
    range_value = config["strike_range"]["range"]

    with open('bfoconfig.json', 'r') as config_file:
        config = json.load(config_file)

    for value in lists:
        instrument = []
        xts = XTSlogin(root_url)
        with open('secret.json', 'r') as file:
            credentials = json.load(file)
            app_key = credentials.get("app_key")
            secret_key = credentials.get("secret_key")

            if not app_key or not secret_key:
                print("Error: Missing app_key or secret_key in the file.")

        token, userid = xts.market_login(secret_key,app_key)
        print(token)
        instrument.append(value)
        strike_value = xts.get_quotes(lists,token)
        strike_value = 22000
        print("STRIKE VALUE")
        print(strike_value)

        percent_range = (strike_value * (range/100))

        expiry_str = config[value]["expiry"]
        existing_strike_value = config[value]['instrument_price']
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
        if datetime.now().date() > expiry_date.date():
            print(f"{value} expired, resetting values.")
            config[value]["min_value"] = float('inf')
            config[value]["max_value"] = float('-inf')
            config[value]["expiry"] = (datetime.now().replace(day=1).date()).strftime("%Y-%m-%d")
            config[value]['instrument_price'] = strike_value

        if existing_strike_value != None:
            if strike_value > existing_strike_value:
            # Calculate the min and max range
                min_range = config[value]["min_value"]
                max_range = int(strike_value + percent_range)
                config[value]["max_value"] = max_range
                config[value]["instrument_price"] = strike_value
                print(min_range)
                print(max_range)
            
            elif strike_value < existing_strike_value:
                min_range = int(strike_value - percent_range)
                max_range = config[value]["max_value"]
                config[value]["min_value"] = min_range
                config[value]["instrument_price"] = strike_value
                print(min_range)
                print(max_range)
            
            else:
                min_range = int(strike_value - percent_range)
                max_range = int(strike_value + percent_range)
                print(min_range)
                print(max_range)
                config[value]["min_value"] = min_range
                config[value]["max_value"] = max_range
                config[value]["instrument_price"] = strike_value
        else:
            min_range = int(strike_value - percent_range)
            max_range = int(strike_value + percent_range)
            print(min_range)
            print(max_range)
            config[value]["min_value"] = min_range
            config[value]["max_value"] = max_range
            config[value]["instrument_price"] = strike_value


        # Write to config.json
        with open('bfoconfig.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)

        print("Min and Max ranges saved to config.json")
        df['UnderlyingIndexName'] = df['UnderlyingIndexName'].str.upper()

        df['ContractExpiration'] = pd.to_datetime(df['ContractExpiration']).dt.date

        # Filter the DataFrame for 'IO' and the current 'UnderlyingIndexName'

        # Get unique StrikePrices (as strings)
        filtered_df = df[(df['Series'] == 'IO') & (df['UnderlyingIndexName'] == value)]
        unique_strikes = filtered_df['StrikePrice'].drop_duplicates().tolist()
        #print(unique_strikes)
        filtered_strikes = [strike for strike in unique_strikes if min_range <= float(strike) <= max_range]

        # Print the filtered strikes
        print("Filtered Strikes within range:", filtered_strikes)
        # Iterate over unique strike prices
        for strike in filtered_strikes:
            
                # Filter for OptionType = 3 (CE) for each StrikePrice
            ce_option_data = filtered_df[
                ((filtered_df['StrikePrice'] == strike) &
                (filtered_df['OptionType'] == 3))]

            pe_option_data = filtered_df[
                ((filtered_df['StrikePrice'] == strike) &
                (filtered_df['OptionType'] == 4))]
                    # Sort by ContractExpiration (to ensure chronological order)
            sorted_ce_data = ce_option_data.sort_values(by='ContractExpiration')
            sorted_pe_data = pe_option_data.sort_values(by='ContractExpiration')
                
            print(sorted_ce_data)
            print(sorted_pe_data)
                # Ensure there are enough rows before selecting them

            if value != "SENSEX":
                # Select top 2 rows for CE and PE
                top_2_ce_rows = sorted_ce_data.head(2)
                top_2_pe_rows = sorted_pe_data.head(2)

                # Append top 2 CE rows
                for df_subset in [top_2_ce_rows]:
                    result = df_subset[['ExchangeInstrumentID', 'InstrumentType']]
                    result_df = pd.DataFrame(result)
                    result_dict = result_df.to_dict(orient='records')
                    #print(result_dict)
                    for entry in result_dict:
                        if 'ExchangeInstrumentID' in entry:
                            entry['exchangeInstrumentID'] = entry.pop('ExchangeInstrumentID', None)
                        if 'InstrumentType' in entry:
                            entry['exchangeSegment'] = entry.pop('InstrumentType', None)
                    result_list.extend(result_dict)

                # Append top 2 PE rows
                for df_subset in [top_2_pe_rows]:
                    result = df_subset[['ExchangeInstrumentID', 'InstrumentType']]
                    result_df = pd.DataFrame(result)
                    result_dict = result_df.to_dict(orient='records')
                    #print(result_dict)
                    for entry in result_dict:
                        if 'ExchangeInstrumentID' in entry:
                            entry['exchangeInstrumentID'] = entry.pop('ExchangeInstrumentID', None)
                        if 'InstrumentType' in entry:
                            entry['exchangeSegment'] = entry.pop('InstrumentType', None)
                    result_list.extend(result_dict)    
            
            else:
                current_ce_week_exp = sorted_ce_data.iloc[[0]]
                next_ce_week_exp = sorted_ce_data.iloc[[1]]
                current_ce_month_exp = sorted_ce_data.iloc[[2]]
                next_ce_month_exp = sorted_ce_data.iloc[[3]]

                current_pe_week_exp = sorted_pe_data.iloc[[0]]
                next_pe_week_exp = sorted_pe_data.iloc[[1]]
                current_pe_month_exp = sorted_pe_data.iloc[[2]]
                next_pe_month_exp = sorted_pe_data.iloc[[3]]

                
                for df_subset, label in [
                    (current_ce_week_exp, "current_ce_week_exp"),
                    (next_ce_week_exp, "next_ce_week_exp"),
                    (current_ce_month_exp, "current_ce_month_exp"),
                    (next_ce_month_exp, "next_ce_month_exp"),
                    (current_pe_week_exp, "current_pe_week_exp"),
                    (next_pe_week_exp, "next_pe_week_exp"),
                    (current_pe_month_exp, "current_pe_month_exp"),
                    (next_pe_month_exp, "next_pe_month_exp")
                ]:
                    # Select specific columns
                    result = df_subset[['ExchangeInstrumentID', 'InstrumentType']]

                    # Convert the result (Series) to a DataFrame and then to a list of dictionaries
                    result_df = pd.DataFrame(result)  # Convert to DataFrame
                    result_dict = result_df.to_dict(orient='records')  # Convert DataFrame to list of dicts
                    
                    # Debug: Print the result_dict to inspect the structure
                    print(result_dict)

                    # Rename keys and ensure correct structure
                    for entry in result_dict:
                        if 'ExchangeInstrumentID' in entry:  # Check if the key exists
                            entry['exchangeInstrumentID'] = entry.pop('ExchangeInstrumentID', None)
                        if 'InstrumentType' in entry:  # Check if the key exists
                            entry['exchangeSegment'] = entry.pop('InstrumentType', None)

                            # Append to the final result list
                    result_list.extend(result_dict)

    return result_list 


    #INDEX DATA SHOULD ALSO BE CONSIDERED
    #SUBSCRIPTION LIST , NAME SHOULD BE IN CSV FILE

def get_nfo_liquid_strikes(values):
    df = pd.read_csv('op.csv', low_memory=False)
    new_list = []
    for value in values:
        parts = value.split()

        # Extract the individual components
        symbol = parts[0]       # NIFTY
        date = parts[1]         # 26DEC2024
        option_type = parts[2]  # PE
        strike_price = parts[3] # 30750

        # Format the components into the desired format
        formatted_string = f"OPTIDX{symbol}{date[:2]}-{date[2:5]}-{date[5:]}{option_type}{strike_price}"
        match_row = df[df['CONTRACT_D'] == formatted_string]

        if not match_row.empty:
            # Return the TRADED_QUA value
            if(match_row['TRADED_QUA'].values[0]) > 2000:
                #print(match_row['TRADED_QUA'].values[0])
                new_list.append(value)
    return new_list

def gen_overall_csv():
    result = []

    # Read the JSON file containing the subscription data
    with open('subscription_list.json', 'r') as file:
        try:
            data_from_file = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

    # Read the CSV files (nsfo.csv and bfo.csv)
    try:
        nsfo_df = pd.read_csv('nfo.csv')
        bfo_df = pd.read_csv('bfo.csv')
    except FileNotFoundError as e:
        print(f"Error reading CSV files: {e}")
        return

    # Loop through each data entry from the JSON file
    for data in data_from_file:
        try:
            # Extract exchangeInstrumentID from the JSON data
            exchange_instrument_id = data.get("exchangeInstrumentID")
            if exchange_instrument_id is None:
                print(f"Missing 'exchangeInstrumentID' in data: {data}")
                continue

            print(f'Processing exchangeInstrumentID: {exchange_instrument_id}')
            
            # Check for a match in nsfo_df
            nsfo_match = nsfo_df[nsfo_df['ExchangeInstrumentID'] == exchange_instrument_id]
            
            if not nsfo_match.empty:  # If a match is found in nsfo.csv
                result.append({
                    'ExchangeInstrumentID': exchange_instrument_id,
                    'ExchangeSegment': nsfo_match['InstrumentType'].values[0],
                    'DisplayName': nsfo_match['DisplayName'].values[0],
                    'Name': nsfo_match['Name'].values[0]
                })
            else:
                # If no match found in nsfo.csv, check bfo_df
                bfo_match = bfo_df[bfo_df['ExchangeInstrumentID'] == exchange_instrument_id]
                if not bfo_match.empty:  # If a match is found in bfo.csv
                    result.append({
                        'ExchangeInstrumentID': exchange_instrument_id,
                        'ExchangeSegment': bfo_match['InstrumentType'].values[0],
                        'DisplayName': bfo_match['DisplayName'].values[0],
                        'Name': bfo_match['Name'].values[0]
                    })

        except KeyError as e:
            print(f"Key error processing data: {e}")
            continue

    # If result is empty, notify the user
    if not result:
        print("No matches found.")
        return

    # Convert result to DataFrame and save to a new CSV file
    result_df = pd.DataFrame(result)
    result_df.to_csv('allInstruments.csv', index=False)

    print("Matched data saved to 'allInstruments.csv'.")



def set_expiry_range():
    nfo_Series = ['NIFTY 50', 'NIFTY MID SELECT', 'NIFTY FIN SERVICE', 'NIFTY BANK']
    bfo_Series = ['BANKEX', 'SENSEX']
    
    # Read data from CSV files
    nsfo_df = pd.read_csv('nfo.csv')
    bfo_df = pd.read_csv('bfo.csv')
    
    # Initialize dictionaries to store the config data
    nfo_config_data = {}
    bfo_config_data = {}

    # Load the existing configuration for NFO (if any) to retain min/max values
    try:
        with open('nfoconfig.json', 'r') as json_file:
            nfo_config_data = json.load(json_file)
    except FileNotFoundError:
        print("No existing nfoconfig.json file found. A new one will be created.")

    # Process NFO series
    for series in nfo_Series:
        # Ensure the series names in the DataFrame are in uppercase
        nsfo_df['UnderlyingIndexName'] = nsfo_df['UnderlyingIndexName'].str.upper()

        # Filter the DataFrame for the given series and options type
        filtered_df = nsfo_df[(nsfo_df['Series'] == 'OPTIDX') & (nsfo_df['UnderlyingIndexName'] == series)]
        
        # Extract unique expiration dates
        all_Dates = filtered_df['ContractExpiration'].drop_duplicates().tolist()

        # Get the last day of the current month
        current_date = datetime.now()
        next_month = current_date.replace(day=28) + timedelta(days=4)
        last_day_of_current_month = next_month - timedelta(days=next_month.day)

        # Convert string dates to datetime
        dates = [datetime.fromisoformat(date) for date in all_Dates]

        # Find the closest date to the last day of the current month
        closest_date = None
        min_diff = timedelta(days=365)  # Initial large difference

        for date in dates:
            if date.month == last_day_of_current_month.month and date.year == last_day_of_current_month.year:
                diff = abs(last_day_of_current_month - date)
                if diff < min_diff:
                    closest_date = date
                    min_diff = diff

        # If series already exists in the config, retain min_value and max_value, else set default
        if series in nfo_config_data:
            existing_config = nfo_config_data[series]
            min_value = existing_config.get("min_value", None)
            max_value = existing_config.get("max_value", None)
            instrument_price = existing_config.get("instrument_price", None)
        else:
            min_value = None
            max_value = None
            instrument_price = None

        # Add or update the expiry date while keeping min_value and max_value intact
        nfo_config_data[series] = {
            "expiry": closest_date.strftime('%Y-%m-%d') if closest_date else "N/A",
            "min_value": min_value,
            "max_value": max_value,
            "instrument_price" : instrument_price
        }

    # Save the updated config data to nfoconfig.json
    with open('nfoconfig.json', 'w') as json_file:
        json.dump(nfo_config_data, json_file, indent=4)

    print("NFO config file created/updated successfully.")

    # Load the existing configuration for BFO (if any) to retain min/max values
    try:
        with open('bfoconfig.json', 'r') as json_file:
            bfo_config_data = json.load(json_file)
    except FileNotFoundError:
        print("No existing bfoconfig.json file found. A new one will be created.")

    # Process BFO series
    for series in bfo_Series:
        # Ensure the series names in the DataFrame are in uppercase
        bfo_df['UnderlyingIndexName'] = bfo_df['UnderlyingIndexName'].str.upper()

        # Filter the DataFrame for the given series and options type
        filtered_df = bfo_df[(bfo_df['Series'] == 'IF') & (bfo_df['UnderlyingIndexName'] == series)]
        
        # Extract unique expiration dates
        all_Dates = filtered_df['ContractExpiration'].drop_duplicates().tolist()

        # Get the last day of the current month
        current_date = datetime.now()
        next_month = current_date.replace(day=28) + timedelta(days=4)
        last_day_of_current_month = next_month - timedelta(days=next_month.day)

        # Convert string dates to datetime
        dates = [datetime.fromisoformat(date) for date in all_Dates]

        # Find the closest date to the last day of the current month
        closest_date = None
        min_diff = timedelta(days=365)  # Initial large difference

        for date in dates:
            if date.month == last_day_of_current_month.month and date.year == last_day_of_current_month.year:
                diff = abs(last_day_of_current_month - date)
                if diff < min_diff:
                    closest_date = date
                    min_diff = diff

        # If series already exists in the config, retain min_value and max_value, else set default
        if series in bfo_config_data:
            existing_config = bfo_config_data[series]
            min_value = existing_config.get("min_value", None)
            max_value = existing_config.get("max_value", None)
            instrument_price = existing_config.get("instrument_price", None)
        else:
            min_value = None
            max_value = None
            instrument_price = None

        # Add or update the expiry date while keeping min_value and max_value intact
        bfo_config_data[series] = {
            "expiry": closest_date.strftime('%Y-%m-%d') if closest_date else "N/A",
            "min_value": min_value,
            "max_value": max_value,
            "instrument_price" : instrument_price
        }

    # Save the updated config data to bfoconfig.json
    with open('bfoconfig.json', 'w') as json_file:
        json.dump(bfo_config_data, json_file, indent=4)

    print("BFO config file created/updated successfully.")



# Output the result
def last_day_of_month(date):
    # Get the last day of the month by moving to the next month and subtracting one day
    next_month = date.replace(day=28) + timedelta(days=4)  # this will always land in the next month
    last_day = next_month - timedelta(days=next_month.day)
    return last_day

def add_nfo_data():
    data_list = []

    # Append the data
    data_list.append({'exchangeInstrumentID': 26000, 'exchangeSegment': 1})
    data_list.append({'exchangeInstrumentID': 26001, 'exchangeSegment': 1})

    # Print the list to verify
    print(data_list)
    return data_list


def main():
    generate_nfo()
    generate_bhavcopy()

    set_expiry_range()
    data_list = add_nfo_data()
    nfo_future_list = get_nfo_futures_data()
    #bfo_future_list = get_bfo_futures_data()
    nfo_option_list = get_nfo_op_data()
    #bfo_option_list = get_bfo_op_data()

    #combined_data = nfo_future_list + bfo_future_list + nfo_option_list + bfo_option_list
    combined_data = data_list + nfo_future_list + nfo_option_list
    # Write the combined data to the JSON file
    unique_data = list({(item['exchangeInstrumentID'], item['exchangeSegment']): item for item in combined_data}.values())
    unique_data = unique_data[:800]
    # Write the unique data to the JSON file
    # with open('subscription_list.json', 'a') as json_file:
    #     json.dump(unique_data, json_file, indent=4)


    file_path = 'subscription_list.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            try:
                existing_data = json.load(json_file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data_set = {json.dumps(item, sort_keys=True) for item in existing_data}
    new_data = [item for item in unique_data if json.dumps(item, sort_keys=True) not in existing_data_set]

    merged_data = existing_data + new_data

    with open(file_path, 'w') as json_file:
        json.dump(merged_data, json_file, indent=4)

    print(f"Data saved to {file_path}")

    print(f"list of unique data length is {len(merged_data)}")
    print("Unique combined data successfully saved to subscription_list.json")

    gen_overall_csv()
    print(f"total length of unique combinations is {len(unique_data)}")
    
if __name__ == '__main__':
    main()
