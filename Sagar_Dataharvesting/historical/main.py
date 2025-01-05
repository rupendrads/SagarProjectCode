import pandas as pd
from datetime import datetime, timedelta
import json
from io import StringIO
import time
import urllib3
from broker import XTSlogin
from sqlalchemy import create_engine
from helpers import create_table

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
        # self.xts.update_master_db() 
        self.logger = Logger('historical_instruments.txt')
        print(f'Logged in with user ID: {self.userid}')

    def convert_to_string_datetime(self, timestamp):
        current_time = datetime.now()
        combined_datetime = current_time.replace(hour=int(timestamp.split(":")[0]), minute=int(timestamp.split(":")[1]), second=0)
        formatted_datetime = combined_datetime.strftime("%b %d %Y %H%M%S")
        return formatted_datetime
    
    def convert_to_datetime(self,timestamp):
        datetime_object = datetime.strptime(timestamp, "%b %d %Y %H%M%S")
        return datetime_object
    
    def read_instrument_file(self, file_path, segment_type):
        df = pd.read_csv(file_path, low_memory=False)
        if segment_type ==1:
            df = df[df["Series"].isin(["EQ"])]
            eq_instrument_names = list(set(df["Description"]))
            df = df[df['Description'].isin(eq_instrument_names)]
        else:
            df = df[df["Series"].isin(["FUTSTK", "FUTIDX"])]
            fut_instrument_names = list(set(df.UnderlyingIndexName))
            filtered_df = df[df['UnderlyingIndexName'].isin(fut_instrument_names)]
            sorted_df = filtered_df.sort_values(by=['UnderlyingIndexName', 'ContractExpiration'])
            df = sorted_df.drop_duplicates(subset='UnderlyingIndexName')
        df = df[['Description', 'ExchangeInstrumentID']]
        df.set_index('Description', inplace=True, drop=True)
        return df.to_dict()

    def fetch_and_store_historical_data(self, instrument_data, exchange_segment):
        start_time = self.convert_to_datetime(self.config['start_time'])
        end_time = self.convert_to_datetime(self.config['end_time'])
        print(start_time, end_time)
        instrument_to_download = list(pd.read_csv('data.csv')["0"])
        filtered_instruments = {
            key: value for key, value in instrument_data['ExchangeInstrumentID'].items()
            if key in instrument_to_download
        }
        instrument_data['ExchangeInstrumentID'] = filtered_instruments        
        compression_value = self.config['compressionValue']
        current_start_time = start_time
        while current_start_time < end_time:
            current_end_time = min(current_start_time + timedelta(days=100), end_time)

            for name, instrument in instrument_data['ExchangeInstrumentID'].items():
                params = {
                    'exchangeSegment': exchange_segment,
                    'exchangeInstrumentID': instrument,
                    'startTime': current_start_time.strftime('%b %d %Y %H%M%S'),
                    'endTime': current_end_time.strftime('%b %d %Y %H%M%S'),
                    'compressionValue': compression_value
                }
                print(params)
                try:
                    response = self.xts.get_historical_data(params)['result']['dataReponse']
                    response = response.replace(',', '\n')
                    historical_data = pd.read_csv(StringIO(response), sep='|', usecols=range(7), header=None, low_memory=False)
                    historical_data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi']
                    historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'], unit='s')
                    historical_data['instrument_token'] = instrument
                    historical_data['tradingsymbol'] = name
                    historical_data['segment'] = exchange_segment
                    self.insert_dataframe_to_sql(historical_data)
                    print(f'Updated database for {name}')
                    
                except Exception as e:
                    self.logger.log(f"Failed to retrieve historical data for {name}: {e}")
                    # print(f"Failed to retrieve historical data for {name}: {e}")
            # break
            current_start_time += timedelta(days=101) 

            # time.sleep(1)

    @staticmethod
    def insert_dataframe_to_sql(df):
        today_date = datetime.now().strftime("%d%m%Y")
        table_name = f"historical"
        # print(table_name)
        database_url = "mysql+mysqlconnector://root:pegasus@localhost/sagar_dataharvesting"        
        engine = create_engine(database_url)
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

        print(f"Data successfully inserted into {table_name}")

def main():
    create_table()
    historical_data_handler = HistoricalData('config.json', 'secret.json')
    equity_data = historical_data_handler.read_instrument_file('nsecm.csv', 1)
    # equity_data["ExchangeInstrumentID"] = pd.read_csv("data.csv")
    # fno_data = historical_data_handler.read_instrument_file('nfo.csv', 2)
    historical_data_handler.fetch_and_store_historical_data(equity_data, 1)
    # historical_data_handler.fetch_and_store_historical_data(fno_data, 2)

if __name__ == "__main__":
    main()
