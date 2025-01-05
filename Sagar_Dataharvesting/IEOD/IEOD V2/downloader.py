import pandas as pd
from datetime import datetime, timedelta
import json
from io import StringIO
import time
import urllib3
from broker import XTSlogin
from sqlalchemy import create_engine
from helpers import create_table
from utils import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ConfigManager:
    @staticmethod
    def load_config(filename):
        with open(filename, 'r') as f:
            return json.load(f)

class Logger:
    def __init__(self, file_name):
        self.file_name = file_name

    def log(self, message):
        with open(self.file_name, 'a') as f:
            f.write(f"{datetime.now()}: {message}\n")

class HistoricalData:
    def __init__(self, config_file, secret_file):
        self.config = ConfigManager.load_config(config_file)
        self.creds = ConfigManager.load_config(secret_file)
        self.xts = XTSlogin()
        self.market_token, self.userid = self.xts.market_login(self.creds['secret_key'], self.creds['app_key'])
        self.xts.update_master_db()
        self.logger = Logger('historical_instruments.txt')
        print(f'Logged in with user ID: {self.userid}')
        self.failed_download_count = 0 
    def convert_datetime(self, timestamp):
        current_time = datetime.now() - timedelta(days=1)
        combined_datetime = current_time.replace(hour=int(timestamp.split(":")[0]), minute=int(timestamp.split(":")[1]), second=0)
        formatted_datetime = combined_datetime.strftime("%b %d %Y %H%M%S")
        return formatted_datetime
    
    def read_instrument_file(self, file_path, segment_type):
        df = pd.read_csv(file_path, low_memory=False)
        if segment_type ==1:
            total_nifty = pd.read_csv("nifty_total_market.csv")
            total_nifty = total_nifty.iloc[1:].reset_index(drop=True)
            stocks_list = list(total_nifty['SYMBOL \n'])
            df = df[
                    ((df['Name'].isin(stocks_list)) & 
                    ((df['Series'].isin(['EQ', 'BE'])) )| (df['Series'] == 'GB'))
                ]
            eq_instrument_names = list(set(df["Description"]))
            df = df[df['Description'].isin(eq_instrument_names)]
            print(f"total number of instruments in equity and gold bonds is {len(df)}")
        else:
            # df = df[df["Series"].isin(["FUTSTK", "FUTIDX"])]
            # fut_instrument_names = list(set(df.UnderlyingIndexName))
            # filtered_df = df[df['UnderlyingIndexName'].isin(fut_instrument_names)]
            # sorted_df = filtered_df.sort_values(by=['UnderlyingIndexName', 'ContractExpiration'])
            # df = sorted_df.drop_duplicates(subset='UnderlyingIndexName')
            df = df[df["Series"].isin(["FUTSTK","FUTIDX"])]
            df = df[df['UnderlyingIndexName'].notna()]
            print(f"total number of futures for current/next/far is {len(df)}")
        
        df = df[['Description', 'ExchangeInstrumentID']]
        df.set_index('Description', inplace=True, drop=True)
        return df.to_dict()

    def fetch_and_store_historical_data(self, instrument_data, exchange_segment):
        start_time = self.convert_datetime(self.config['start_time'])
        end_time = self.convert_datetime(self.config['end_time'])
        # print(start_time)
        compression_value = self.config['compressionValue']

        for name, instrument in instrument_data['ExchangeInstrumentID'].items():
            params = {
                'exchangeSegment': exchange_segment,
                'exchangeInstrumentID': instrument,
                'startTime': start_time,
                'endTime': end_time, 
                'compressionValue': compression_value
            }
            # print(params)
            try:
                response = self.xts.get_historical_data(params)['result']['dataReponse']
                response = response.replace(',', '\n')
                historical_data = pd.read_csv(StringIO(response), sep='|', usecols=range(7), header=None, low_memory=False)
                historical_data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi']
                historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'], unit='s')
                historical_data['instrument_token'] = instrument
                historical_data['tradingsymbol'] = name
                historical_data['segment'] = exchange_segment
                if not len(historical_data):
                    self.logger.log(f"No data available for {name} for the specified time period.")
                else:
                    self.insert_dataframe_to_sql(historical_data)
                    print(f'Updated database for {name}')
                # print(historical_data)
                
            except Exception as e:
                self.logger.log(f"{name}: {e}")
                self.failed_download_count +=1
            # time.sleep(1)  

    @staticmethod
    def insert_dataframe_to_sql(df):
        today_date = datetime.now().strftime("%d%m%Y")
        table_name = f"ieod_{today_date}"
        # print(table_name)
        database_url = "mysql+mysqlconnector://root:pegasus@localhost/sagar_dataharvesting"        
        engine = create_engine(database_url)
            
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

        print(f"Data successfully inserted into {table_name}")

def main():
    create_table()
    historical_data_handler = HistoricalData('config.json', 'secret.json')
    indices = get_indices_dict()
    
    indices_ltp_response = historical_data_handler.xts.get_quotes(indices)
    print(indices_ltp_response)
    #indices strike ranges
    indices_options = process_indices_ltp_response(indices_ltp_response)
    #equity and GB
    equity_data = historical_data_handler.read_instrument_file('nsecm.csv', 1)

    #futures data for both stock and indices
    futures_data = historical_data_handler.read_instrument_file('nfo.csv', 2)
    stock_options_data ={}
    #stock options
    stock_options_data['ExchangeInstrumentID'] = fetch_and_process_options_data()
    # historical_data_handler.fetch_and_store_historical_data(stock_options_data, 2)
    # print(historical_data_handler.xts.get_quotes([{'exchangeInstrumentID': 11195, 'exchangeSegment':1}]))
    # historical_data_handler.fetch_and_store_historical_data(equity_data, 1)
    # historical_data_handler.fetch_and_store_historical_data(futures_data, 2)
    # print(f"failed download count is {historical_data_handler.failed_download_count}")
if __name__ == "__main__":
    main()
