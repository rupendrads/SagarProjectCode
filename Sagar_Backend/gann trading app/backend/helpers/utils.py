import pandas as pd
import configparser
from datetime import datetime, timedelta
def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def get_last_trading_day_data(kite, symbol):
    to_date = datetime.now().date()
    from_date  = to_date - timedelta(days=10)
    df = pd.DataFrame(kite.instruments())
    instrument_token = df[(df['tradingsymbol']==symbol) & (df['exchange']=='NSE')].instrument_token.values[0]
    print(df)
    df = pd.DataFrame(kite.historical_data(int(instrument_token), from_date, to_date, 'day'))
    return df[-1:].close.values[0],pd.to_datetime(df[-1:].date.values[0]).date()

def convert_to_datetime(date_str):
    date_format = "%d/%m/%Y"
    datetime_obj = datetime.strptime(date_str, date_format)
    return datetime_obj.date()