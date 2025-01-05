import json
import os
import pandas as pd
import requests
import zipfile
from io import StringIO
import json
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