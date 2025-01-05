import pandas as pd
from datetime import datetime, timedelta
import json
from io import StringIO
import urllib3
from broker import XTSlogin
from sqlalchemy import create_engine, text
from constants import *
from typing import Dict, Any
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""Loads configuration from a JSON file."""
class ConfigManager:
    @staticmethod
    def load_config(filename: str) -> Dict[str, Any]:
        with open(filename, 'r') as f:
            return json.load(f)
    
    """Saves configuration to a JSON file."""
    @staticmethod
    def save_config(filename: str, config: Dict[str, Any]) -> None:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)

"""Logs a message with the current timestamp to a file."""
class Logger:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def log(self, message: str) -> None:
        with open(self.file_name, 'a') as f:
            f.write(f"{datetime.now()}: {message}\n")

class HistoricalData:
    """Initializes the HistoricalData object with configurations and credentials."""
    def __init__(self, config_file: str, secret_file: str):
        self.config_file = config_file
        self.config = ConfigManager.load_config(config_file)
        self.creds = ConfigManager.load_config(secret_file)
        self.xts = XTSlogin()
        self.market_token, self.userid = self.xts.market_login(self.creds['secret_key'], self.creds['app_key'])
        self.logger = Logger('historical_instruments.txt')
        print(f'Logged in with user ID: {self.userid}')
        self.database_url = f"mysql+mysqlconnector://{USERNAME}:{DB_PASSWORD}@{HOST}/{DB_NAME}"
        self.engine = create_engine(self.database_url)
        self.create_index_update_data_table()
        self.validate_date_format()

    """Creates the index_update_data table if it does not exist."""
    def create_index_update_data_table(self) -> None:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS index_update_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            end_time VARCHAR(20) NOT NULL
        );
        """
        with self.engine.connect() as connection:
            connection.execute(text(create_table_query))

    """Converts a timestamp string to a formatted datetime string."""
    def convert_to_string_datetime(self, timestamp: str) -> str:
        current_time = datetime.now()
        combined_datetime = current_time.replace(hour=int(timestamp.split(":")[0]), minute=int(timestamp.split(":")[1]), second=0)
        formatted_datetime = combined_datetime.strftime("%b %d %Y %H%M%S")
        return formatted_datetime
    
    """Converts a formatted datetime string to a datetime object."""
    def convert_to_datetime(self, timestamp: str) -> datetime:
        datetime_object = datetime.strptime(timestamp, "%b %d %Y %H%M%S")
        return datetime_object
    
    """Validates the date format in the configuration file."""
    def validate_date_format(self) -> None:
        date_fields = ['start_time', 'end_time']
        for field in date_fields:
            date_str = self.config.get(field, '')
            try:
                datetime.strptime(date_str, "%b %d %Y %H%M%S")
            except ValueError:
                raise ValueError(f"Invalid date format for {field}: {date_str}. Expected format: 'MMM DD YYYY HHMMSS'")
    
    """Reads instrument data from a CSV file and filters based on the segment type."""
    def read_instrument_file(self, file_path: str, segment_type: int) -> Dict[str, int]:
        df = pd.read_csv(file_path, low_memory=False)
        if segment_type == 1:
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

    """Fetches and stores historical data for the specified exchange segment."""
    def fetch_and_store_historical_data(self, exchange_segment: int) -> None:
        start_time = self.convert_to_datetime(self.config['start_time'])
        end_time = self.convert_to_datetime(self.config['end_time'])
        filtered_instruments = INSTRUMENTS_LIST
        instrument_data = {'ExchangeInstrumentID': filtered_instruments}
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
                # print(params)
                try:
                    response = self.xts.get_historical_data(params)['result']['dataReponse']
                    response = response.replace(',', '\n')
                    historical_data = pd.read_csv(StringIO(response), sep='|', usecols=range(7), header=None, low_memory=False)
                    historical_data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi']
                    historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'], unit='s')
                    historical_data['timestamp'] = historical_data['timestamp'].apply(lambda x: x.replace(second=0))
                    historical_data['instrument_token'] = instrument
                    historical_data['tradingsymbol'] = name
                    historical_data['segment'] = exchange_segment
                    self.insert_dataframe_to_sql(historical_data, name)
                    print(f'Updated database for {name}')
                except Exception as e:
                    self.logger.log(f"Failed to retrieve historical data for {name}: {e}")

            current_start_time += timedelta(days=101) 

    """Inserts a DataFrame into the SQL database."""
    def insert_dataframe_to_sql(self, df: pd.DataFrame, table_suffix: str) -> None:
        table_name = f"{table_suffix}_index"
        df.to_sql(name=table_name, con=self.engine, if_exists='append', index=False)
        print(f"Data successfully inserted into {table_name}")

    @staticmethod
    def store_data_to_file(df: pd.DataFrame, name: str) -> None:
        """Stores DataFrame data to a CSV file."""
        today_date = datetime.now().strftime("%d%m%Y")
        file_name = f"{name}_index_{today_date}.csv"
        df.to_csv(file_name, index=False)
        print(f"Data successfully stored in {file_name}")

    """Updates the start and end times in the configuration file."""
    def update_config_times(self) -> None:
        query = "SELECT MAX(end_time) as end_time FROM index_update_data"
        result = pd.read_sql(query, self.engine)
        
        if not result.empty and result.iloc[0]['end_time']:
            end_time_str = result.iloc[0]['end_time']
            end_time_dt = datetime.strptime(end_time_str, "%b %d %Y %H%M%S")
            start_time_dt = (end_time_dt + timedelta(days=1)).replace(hour=9, minute=15, second=0)
            self.config['start_time'] = start_time_dt.strftime("%b %d %Y %H%M%S")

        new_end_time = datetime.now().strftime("%b %d %Y 153000")
        self.config['end_time'] = new_end_time
        ConfigManager.save_config(self.config_file, self.config)
    """Logs the end time to the index_update_data table."""
    def log_end_time(self) -> None:
        
        data = {'end_time': [self.config['end_time']]}
        df = pd.DataFrame(data)
        df.to_sql(name='index_update_data', con=self.engine, if_exists='append', index=False)

    """Checks if today is a holiday or weekend."""
    def is_holiday(self) -> bool:
        today = datetime.now()
        weekday = today.weekday()  
        if weekday >= 5:  
            return True
        with open('holidays.txt', 'r') as file:
            holidays = [line.strip() for line in file]
        today_str = today.strftime("%d-%b-%Y")
        if today_str in holidays:
            return True
        return False

"""Main function to execute the historical data fetching and storing them."""
def main() -> None:
    try:
        historical_data_handler = HistoricalData('config.json', 'secret.json')
        if historical_data_handler.is_holiday():
            print("Today is market closed. Exiting.")
            return
        historical_data_handler.fetch_and_store_historical_data(1)
        historical_data_handler.log_end_time()
        historical_data_handler.update_config_times()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
