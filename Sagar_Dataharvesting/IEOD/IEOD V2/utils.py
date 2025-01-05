import json
import os
import pandas as pd
import requests
import zipfile
from io import StringIO
import json

def get_etfs():
    with open('etf.json', 'r') as file:
        data = json.load(file)
    etf_list = data["ETF"] 
    df = pd.read_csv('nsecm.csv', low_memory=False)
    filtered_df = df[df['Name'].isin(etf_list)].reset_index(drop=True)
    df_filtered = filtered_df[['Description', 'ExchangeInstrumentID']]
    df_filtered.set_index('Description', inplace=True, drop=True)
    return df_filtered.to_dict()




    # Filter rows where 'Name' is in etf_list
    filtered_df = df[df['Name'].isin(etf_list)].reset_index(drop=True)
def fetch_and_process_options_data():
    url_zip = 'https://nsearchives.nseindia.com/content/fo/fo.zip'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    response = requests.get(url_zip, headers=headers)
    if response.status_code == 200:
        zip_path = 'fo.zip'
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('fo')
        files = os.listdir('fo')
        fno_file = [f for f in files if f.startswith('fo')][0]
        opt_file = [f for f in files if f.startswith('op')][0]

        fno_df = pd.read_csv(f'fo/{fno_file}')
        opt_df = pd.read_csv(f'fo/{opt_file}')
        os.remove(zip_path)
        
        # Filter stock futures
        df = fno_df[fno_df['CONTRACT_D'].str.startswith('FUTSTK')]
        df['Expiry'] = pd.to_datetime(df['CONTRACT_D'].str.extract(r'(\d{2}-\w{3}-\d{4})')[0], format='%d-%b-%Y')
        stock_names = df['CONTRACT_D'].str.replace(r'\d{2}-\w{3}-\d{4}$', '', regex=True).str.replace('FUTSTK', '').tolist()
        
        # Load instrument data and filter options
        instruments = pd.read_csv(r"nfo.csv", low_memory=False)
        stk_options_instruments = instruments[instruments['Series'] == 'OPTSTK']
        
        # Download and process sec_bhavdata_full file
        url_csv = 'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_08112024.csv'
        response = requests.get(url_csv, headers=headers)
        if response.status_code == 200:
            data_str = response.content.decode('utf-8')
            df = pd.read_csv(StringIO(data_str))
            df.columns = df.columns.str.strip()
            df['SERIES'] = df['SERIES'].str.strip()

            # Load existing range data from JSON or create new
            combined_stk_options = {}
            range_data = []
            percentage_range = 10
            file_path = "stk_options_data.json"
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    output_data = json.load(file)
                    range_data = output_data.get("range_data", [])
            else:
                output_data = {"range_data": []}

            # Helper function to find existing stock entry in range_data
            def find_stock_entry(stock_name, range_data):
                for entry in range_data:
                    if entry["name"] == stock_name:
                        return entry
                return None

            # Update range data based on CLOSE_PRICE
            for idx, row in df.iterrows():
                if row['SYMBOL'] in stock_names:
                    lower_range = round(row['CLOSE_PRICE'] * (1 - (percentage_range / 100)))
                    upper_range = round(row['CLOSE_PRICE'] * (1 + (percentage_range / 100)))

                    # Check if stock exists in range_data and update ranges
                    stock_entry = find_stock_entry(row['SYMBOL'], range_data)
                    if stock_entry:
                        if lower_range < stock_entry["lower_range"]:
                            stock_entry["lower_range"] = lower_range
                        if upper_range > stock_entry["upper_range"]:
                            stock_entry["upper_range"] = upper_range
                    else:
                        range_data.append({
                            "name": row['SYMBOL'],
                            "lower_range": lower_range,
                            "upper_range": upper_range
                        })

            output_data["range_data"] = range_data
            with open(file_path, "w") as file:
                json.dump(output_data, file, indent=4)

            with open(file_path, "r") as file:
                updated_data = json.load(file)
                range_data = updated_data.get("range_data", [])

            for idx, row in df.iterrows():
                if row['SYMBOL'] in stock_names:
                    stock_entry = find_stock_entry(row['SYMBOL'], range_data)
                    if stock_entry:
                        lower_range = stock_entry["lower_range"]
                        upper_range = stock_entry["upper_range"]

                        stk_options = stk_options_instruments[stk_options_instruments['Name'] == row['SYMBOL']]
                        stk_options = stk_options[stk_options['ContractExpiration'] == min(stk_options['ContractExpiration'])]
                        stk_options = stk_options[
                            (stk_options['StrikePrice'].astype(float) >= lower_range) & 
                            (stk_options['StrikePrice'].astype(float) <= upper_range)
                        ]
                        stk_options_dict = stk_options.set_index('Description')['ExchangeInstrumentID'].to_dict()
                        combined_stk_options.update(stk_options_dict)
                        
                        
            return combined_stk_options

    else:
        print(f"Failed to download files. Status code: {response.status_code}")
        return None


def filter_indices(df, indices_list):
    
    return df[df['Name'].isin(indices_list)]

def fetch_index_data(exchange_segment):
    url = f'https://ttblaze.iifl.com/apimarketdata/instruments/indexlist?exchangeSegment={exchange_segment}'

    # Send a GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        index_list = data.get("result", {}).get("indexList", [])

        index_data = [{"Name": item.split("_")[0], "ExchangeInstrumentID": item.split("_")[1]} for item in index_list]

        # Convert the list to a DataFrame
        df_index_data = pd.DataFrame(index_data)
        return df_index_data
    else:
        print(f"Failed to fetch data for exchange segment {exchange_segment}. Status code: {response.status_code}")
        return pd.DataFrame()  

def get_indices_dict():
    nse_indices = ['NIFTY 50', 'NIFTY BANK', 'NIFTY MID SELECT', 'NIFTY FIN SERVICE']
    bse_indices = ['SENSEX', 'BANKEX']
    df_segment_1 = fetch_index_data(1)
    df_segment_11 = fetch_index_data(11)
    nse_indices_df = filter_indices(df_segment_1, nse_indices)
    bse_indices_df = filter_indices(df_segment_11, bse_indices)
    nse_indices_dict = [{"exchangeSegment": 1, "exchangeInstrumentID": row['ExchangeInstrumentID']} for _, row in nse_indices_df.iterrows()]
    bse_indices_dict = [{"exchangeSegment": 11, "exchangeInstrumentID": row['ExchangeInstrumentID']} for _, row in bse_indices_df.iterrows()]

    indices_dict = bse_indices_dict + nse_indices_dict
    return indices_dict


import json
import os

import json
import os
import pandas as pd

def process_indices_ltp_response(indices_ltp_response, filename="indices_options.json"):
    instrument_names = [
        {'exchangeInstrumentID': 26065, 'Name': 'SENSEX'},
        {'exchangeInstrumentID': 26118, 'Name': 'BANKEX'},
        {'exchangeInstrumentID': 26000, 'Name': 'NIFTY 50'},
        {'exchangeInstrumentID': 26001, 'Name': 'NIFTY BANK'},
        {'exchangeInstrumentID': 26034, 'Name': 'NIFTY FIN SERVICE'},
        {'exchangeInstrumentID': 26121, 'Name': 'NIFTY MID SELECT'}
    ]
    instrument_name_dict = {item["exchangeInstrumentID"]: item["Name"] for item in instrument_names}

    if os.path.exists(filename):
        with open(filename, "r") as file:
            existing_data = {item["exchangeInstrumentID"]: item for item in json.load(file)}
    else:
        existing_data = {}

    quotes_data = [json.loads(quote) for quote in indices_ltp_response['result']['listQuotes']]
    
    result_data = []
    for quote in quotes_data:
        exchange_instrument_id = int(quote["ExchangeInstrumentID"])
        last_traded_price = round(quote["LastTradedPrice"])
        lower_range = round(last_traded_price * 0.9)
        upper_range = round(last_traded_price * 1.1)
        name = instrument_name_dict.get(exchange_instrument_id, "Unknown")

        if exchange_instrument_id in existing_data:
            existing_entry = existing_data[exchange_instrument_id]
            if lower_range < existing_entry["lower_range"]:
                existing_entry["lower_range"] = lower_range
            if upper_range > existing_entry["upper_range"]:
                existing_entry["upper_range"] = upper_range
            existing_entry["name"] = name
            result_data.append(existing_entry)
        else:
            result_data.append({
                "exchangeInstrumentID": exchange_instrument_id,
                "lower_range": lower_range,
                "upper_range": upper_range,
                "name": name
            })
    
    with open(filename, "w") as file:
        json.dump(result_data, file, indent=4)
    
    with open(filename, "r") as file:
        saved_data = json.load(file)
    
    nfo_df = pd.read_csv('nfo.csv', low_memory=False)
    nfo_df = nfo_df[nfo_df['Series'] == 'OPTIDX']
    combined_filtered_df = pd.DataFrame()
    
    for instrument in saved_data:
        name = instrument["name"]
        
        if name in ["SENSEX", "BANKEX"]:
            continue

        lower_range = instrument["lower_range"]
        upper_range = instrument["upper_range"]
        
        filtered_df = nfo_df[
            (nfo_df['UnderlyingIndexName'].str.upper() == name) &
            (nfo_df['StrikePrice'].astype(int) >= lower_range) &
            (nfo_df['StrikePrice'].astype(int) <= upper_range)
        ]
        
        combined_filtered_df = pd.concat([combined_filtered_df, filtered_df], ignore_index=True)
    
    combined_filtered_df = combined_filtered_df[['Description', 'ExchangeInstrumentID']]
    combined_filtered_df.set_index('Description', inplace=True, drop=True)
    
    return combined_filtered_df.to_dict()
