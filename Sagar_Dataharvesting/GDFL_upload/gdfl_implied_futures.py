# implied_futures_calculator.py
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from constants import *
from helpers import configure_logger, calculate_expiry_sets, forward_fill_implied_futures, calculate_atm_optimized
from constants import *
import numpy as np
import warnings
warnings.filterwarnings("ignore")

'''
Calculates and saves expiry data for the specified instrument.
This function fetches data from the database, processes it to determine
current and monthly expiries for each trading day, and saves the results
both to a CSV file and the database.
'''
def calculate_and_save_expiry_data() -> None:
    '''
    Fetches data from the database for the specified year range.
    Returns a DataFrame containing trading days and expiries.
    '''
    def fetch_data_from_db() -> pd.DataFrame:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(f"USE {db_config['database']};")
        
        all_data: List[pd.DataFrame] = []
        for year in range(START_YEAR, END_YEAR + 1):
            query = f"""
            SELECT DATE(timestamp) as trading_day, expiry FROM {INSTRUMENT_NAME}_{year}
            """
            df = pd.read_sql(query, connection)
            all_data.append(df)
        
        connection.close()
        return pd.concat(all_data, ignore_index=True)

    '''
    Returns the nearest expiry date that is greater than or equal to the given date.
    '''
    def get_nearest_expiry(date: datetime, expiries: List[datetime]) -> Optional[datetime]:
        future_expiries = [exp for exp in expiries if exp >= date]
        return min(future_expiries) if future_expiries else None

    '''
    Returns the monthly expiry for the given date.
    If there's no expiry in the current month after the given date,
    it returns the expiry of the next month.
    '''
    def get_monthly_expiry(date: datetime, expiries: List[datetime]) -> Optional[datetime]:
        month_expiries = [exp for exp in expiries if exp.strftime('%Y-%m') == date.strftime('%Y-%m')]
        if month_expiries:
            if date <= max(month_expiries):
                return max(month_expiries)

        next_month = (date.replace(day=1) + timedelta(days=32)).replace(day=1)
        next_month_expiries = [exp for exp in expiries if exp.strftime('%Y-%m') == next_month.strftime('%Y-%m')]
        return max(next_month_expiries) if next_month_expiries else None

    data = fetch_data_from_db()

    data['trading_day'] = pd.to_datetime(data['trading_day'])
    data['expiry'] = pd.to_datetime(data['expiry'])

    trading_days: List[datetime] = sorted(data['trading_day'].unique())
    all_expiries: List[datetime] = sorted(data['expiry'].unique())
    result = pd.DataFrame(columns=['trading_day', 'current_expiry', 'monthly_expiry', 'symbol'])

    for day in trading_days:
        current_expiry = get_nearest_expiry(day, all_expiries)
        monthly_expiry = get_monthly_expiry(day, all_expiries)

        result = result._append({
            'trading_day': day,
            'current_expiry': current_expiry if current_expiry else pd.NaT,
            'monthly_expiry': monthly_expiry if monthly_expiry else pd.NaT,
            'symbol': INSTRUMENT_NAME
        }, ignore_index=True)

    result['trading_day'] = result['trading_day'].dt.strftime('%Y-%m-%d')
    result['current_expiry'] = result['current_expiry'].dt.strftime('%Y-%m-%d')
    result['monthly_expiry'] = result['monthly_expiry'].dt.strftime('%Y-%m-%d')

    unusual_current_expiries = []
    for _, row in result.iterrows():
        trading_day = pd.to_datetime(row['trading_day'])
        current_expiry = pd.to_datetime(row['current_expiry'])
        days_diff = (current_expiry - trading_day).days
        
        if days_diff > 7:
            unusual_current_expiries.append({
                'trading_day': row['trading_day'],
                'current_expiry': row['current_expiry'],
                'days_diff': days_diff
            })

    if unusual_current_expiries:
        print("Unusual current expiries detected (more than 7 days difference):")
        for entry in unusual_current_expiries:
            print(f"Trading day: {entry['trading_day']}, Current expiry: {entry['current_expiry']}, "
                  f"Difference: {entry['days_diff']} days")
    else:
        print("No unusual current expiries detected.")

    unusual_monthly_expiries = []
    for _, row in result.iterrows():
        trading_day = pd.to_datetime(row['trading_day'])
        last_day_of_month = trading_day + pd.offsets.MonthEnd(0)
        monthly_expiry = pd.to_datetime(row['monthly_expiry'])
        days_diff = (monthly_expiry - last_day_of_month).days
        
        if days_diff < -6 or days_diff > 31:
            unusual_monthly_expiries.append({
                'trading_day': row['trading_day'],
                'monthly_expiry': row['monthly_expiry'],
                'last_day_of_month': last_day_of_month.strftime('%Y-%m-%d'),
                'days_diff': days_diff
            })

    if unusual_monthly_expiries:
        print("Unusual monthly expiries detected:")
        for entry in unusual_monthly_expiries:
            print(f"Trading day: {entry['trading_day']}, Monthly expiry: {entry['monthly_expiry']}, "
                  f"Last day of month: {entry['last_day_of_month']}, Difference: {entry['days_diff']} days")
    else:
        print("No unusual monthly expiries detected.")

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    result.to_csv(f'{INSTRUMENT_NAME}_expiry_data.csv', index=False)
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {EXPIRY_TABLE_NAME} (
        trading_day DATE,
        current_expiry DATE,
        monthly_expiry DATE,
        symbol VARCHAR(10),
        PRIMARY KEY (trading_day)
    )
    """
    cursor.execute(create_table_query)

    insert_query = f"""
    INSERT INTO {EXPIRY_TABLE_NAME} (trading_day, current_expiry, monthly_expiry, symbol)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    current_expiry = VALUES(current_expiry),
    monthly_expiry = VALUES(monthly_expiry),
    symbol = VALUES(symbol)
    """
    data_to_insert = result.values.tolist()
    cursor.executemany(insert_query, data_to_insert)

    connection.commit()
    cursor.close()
    connection.close()

    print(f"Daily expiry data saved to {INSTRUMENT_NAME}_daily_expiry_data.csv")

'''
A class for calculating implied futures prices based on option data.
This class handles data fetching, processing, and calculation of
implied futures prices for both weekly and monthly expiries.
'''
class ImpliedFuturesCalculator:

    '''
    Initializes the ImpliedFuturesCalculator with necessary configurations and data.
    '''
    def __init__(self, instrument_name: str, start_date: str, end_date: str, strike_difference: int) -> None:
        global INSTRUMENT_NAME, START_DATE, END_DATE
        INSTRUMENT_NAME = instrument_name
        START_DATE = start_date
        END_DATE = end_date
        self.strike_difference = int(strike_difference)
        self.logger = configure_logger(LOG_FILE_NAME)
        self.connection = mysql.connector.connect(**db_config)
        self.cursor = self.connection.cursor()
        self.df: pd.DataFrame = pd.DataFrame()
        self.start_year: int = int(START_DATE[:4])
        self.end_year: int = int(END_DATE[:4])
        self.expiry_data: pd.DataFrame = self.read_expiry_data_from_db()
        print(self.expiry_data)
        self.expiry_data['trading_day'] = pd.to_datetime(self.expiry_data['trading_day'])
        self.expiry_data['current_expiry'] = pd.to_datetime(self.expiry_data['current_expiry'])
        self.expiry_data['monthly_expiry'] = pd.to_datetime(self.expiry_data['monthly_expiry'])

    '''
    Reads expiry data from the database for the specified instrument.
    Returns a DataFrame containing the expiry data.
    '''
    def read_expiry_data_from_db(self) -> pd.DataFrame:
        try:
            conn = mysql.connector.connect(**db_config)
            query = f"SELECT * FROM {EXPIRY_TABLE_NAME} WHERE symbol = '{INSTRUMENT_NAME}'"
            expiry_data = pd.read_sql(query, conn)
            conn.close()
            return expiry_data
        except mysql.connector.Error as err:
            print(f"Error reading expiry data from database: {err}")
            return pd.DataFrame()
        
    '''
    Fetches option and futures data from the database for the specified date range.
    Returns three DataFrames: one for call options, one for put options, and one for futures.
    '''
    def fetch_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        ce_data = pd.DataFrame()
        pe_data = pd.DataFrame()
        fut_data = pd.DataFrame()

        for year in range(self.start_year, self.end_year + 1):
            ce_table = f"{INSTRUMENT_NAME}_{year}"
            pe_table = f"{INSTRUMENT_NAME}_{year}"
            fut_table = f"{INSTRUMENT_NAME}_fut"

            if year == self.start_year == self.end_year:
                ce_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {ce_table} WHERE type='CE' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{END_DATE}'"
                pe_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {pe_table} WHERE type='PE' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{END_DATE}'"
                fut_query = f"SELECT timestamp, symbol, type, open, high, low, close FROM {fut_table} WHERE type='FUT' AND expiry ='I' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{END_DATE}'"
                print(ce_query)
                print(pe_query)
                print(fut_query)
            elif year == self.start_year:
                year_end_date = f"{year}-12-31"
                ce_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {ce_table} WHERE type='CE' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{year_end_date}'"
                pe_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {pe_table} WHERE type='PE' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{year_end_date}'"
                fut_query = f"SELECT timestamp, symbol, type, open, high, low, close FROM {fut_table} WHERE type='FUT' AND expiry ='I' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{year_end_date}'"
            elif year == self.end_year:
                year_start_date = f"{year}-01-01"
                ce_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {ce_table} WHERE type='CE' AND DATE(timestamp) BETWEEN '{year_start_date}' AND '{END_DATE}'"
                pe_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {pe_table} WHERE type='PE' AND DATE(timestamp) BETWEEN '{year_start_date}' AND '{END_DATE}'"
                fut_query = f"SELECT timestamp, symbol, type, open, high, low, close FROM {fut_table} WHERE type='FUT' AND expiry ='I' AND DATE(timestamp) BETWEEN '{year_start_date}' AND '{END_DATE}'"
            else:
                ce_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {ce_table} WHERE type='CE'"
                pe_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {pe_table} WHERE type='PE'"
                fut_query = f"SELECT timestamp, symbol, type, open, high, low, close FROM {fut_table} WHERE type='FUT' AND expiry ='I'"


            self.cursor.execute(ce_query)
            ce_data = pd.concat([ce_data, pd.DataFrame(self.cursor.fetchall())], ignore_index=True)
            self.cursor.execute(pe_query)
            pe_data = pd.concat([pe_data, pd.DataFrame(self.cursor.fetchall())], ignore_index=True)
            self.cursor.execute(fut_query)
            fut_data = pd.concat([fut_data, pd.DataFrame(self.cursor.fetchall())], ignore_index=True)
            

        return ce_data, pe_data, fut_data

    '''
    Calculates implied futures prices for both weekly and monthly expiries.
    Updates the main DataFrame with the calculated values.
    '''
    def calculate_implied_futures(self, ce_data: pd.DataFrame, pe_data: pd.DataFrame) -> None:
        print(f"entered calculate implied futures with strike difference as {self.strike_difference}")
        # self.df['atm'] = (round(self.df['close'] / self.strike_difference) * self.strike_difference).astype(int)
        self.df['atm'] = (self.df['close'] / self.strike_difference).round() * self.strike_difference
        self.df['atm'] = self.df['atm'].astype(int)

        print("passed the test")
        for idx, row in self.df.iterrows():
            timestamp: pd.Timestamp = row['timestamp']
            atm: int = row['atm']
            ce_data_filtered = ce_data[(ce_data['timestamp'] == timestamp) & (ce_data['strike'] == atm)]
            pe_data_filtered = pe_data[(pe_data['timestamp'] == timestamp) & (pe_data['strike'] == atm)]

            try:
                ce_min_expiry = self.expiry_data.loc[self.expiry_data['trading_day'].dt.date == timestamp.date(), 'current_expiry'].dt.date.values[0]
                pe_min_expiry = pd.Timestamp(ce_min_expiry)
                ce_min_expiry = pd.Timestamp(ce_min_expiry)
                self.calculate_implied_futures_weekly(ce_min_expiry, pe_min_expiry, ce_data_filtered, pe_data_filtered, idx, atm, timestamp)
            except Exception as e:
                self.logger.error(f"Error processing weekly implied futures at {timestamp}: {e}")

            try:
                max_expiry_ce = max_expiry_pe = self.expiry_data.loc[self.expiry_data['trading_day'].dt.date == timestamp.date(), 'monthly_expiry'].dt.date.values[0]
                max_expiry_ce = pd.Timestamp(max_expiry_ce)
                max_expiry_pe = pd.Timestamp(max_expiry_pe)
                if max_expiry_ce and max_expiry_pe:
                    self.calculate_implied_futures_monthly(max_expiry_ce, max_expiry_pe, ce_data_filtered, pe_data_filtered, idx, atm, timestamp)
                else:
                    self.logger.warning(f"Invalid monthly expiries at {timestamp}")
            except Exception as e:
                self.logger.error(f"Error processing monthly implied futures at {timestamp}: {e}")

    '''
    Calculates weekly implied futures prices and updates the main DataFrame.
    '''
    def calculate_implied_futures_weekly(self, ce_min_expiry: pd.Timestamp, pe_min_expiry: pd.Timestamp, ce_data_filtered: pd.DataFrame, pe_data_filtered: pd.DataFrame, idx: int, atm: int, timestamp: pd.Timestamp) -> None:
        if ce_min_expiry == pe_min_expiry:
            ce_close = ce_data_filtered[ce_data_filtered['expiry'] == ce_min_expiry]['close'].values[0]
            ce_symbol = ce_data_filtered[ce_data_filtered['expiry'] == ce_min_expiry]['symbol'].values[0]
            pe_close = pe_data_filtered[pe_data_filtered['expiry'] == pe_min_expiry]['close'].values[0]
            pe_symbol = pe_data_filtered[pe_data_filtered['expiry'] == pe_min_expiry]['symbol'].values[0]
            implied_futures_weekly = round((atm + ce_close - pe_close), 2)
            self.df.loc[idx, 'ce_close_weekly'] = ce_close
            self.df.loc[idx, 'ce_symbol_weekly'] = ce_symbol
            self.df.loc[idx, 'pe_symbol_weekly'] = pe_symbol
            self.df.loc[idx, 'pe_close_weekly'] = pe_close
            self.df.loc[idx, 'implied_futures_weekly'] = implied_futures_weekly
        else:
            self.logger.warning(f"Insufficient data for weekly implied futures at {timestamp}")

    '''
    Calculates monthly implied futures prices and updates the main DataFrame.
    '''
    def calculate_implied_futures_monthly(self, ce_max_expiry: pd.Timestamp, pe_max_expiry: pd.Timestamp, ce_data_filtered: pd.DataFrame, pe_data_filtered: pd.DataFrame, idx: int, atm: int, timestamp: pd.Timestamp) -> None:
        if ce_max_expiry == pe_max_expiry:
            ce_close = ce_data_filtered[ce_data_filtered['expiry'] == ce_max_expiry]['close'].values[0]
            ce_symbol = ce_data_filtered[ce_data_filtered['expiry'] == ce_max_expiry]['symbol'].values[0]
            pe_close = pe_data_filtered[pe_data_filtered['expiry'] == pe_max_expiry]['close'].values[0]
            pe_symbol = pe_data_filtered[pe_data_filtered['expiry'] == pe_max_expiry]['symbol'].values[0]
            implied_futures_monthly = round((atm + ce_close - pe_close), 2)
            self.df.loc[idx, 'implied_futures_monthly'] = implied_futures_monthly
            self.df.loc[idx, 'ce_close_monthly'] = ce_close
            self.df.loc[idx, 'ce_symbol_monthly'] = ce_symbol
            self.df.loc[idx, 'pe_symbol_monthly'] = pe_symbol
            self.df.loc[idx, 'pe_close_monthly'] = pe_close
        else:
            self.logger.warning(f"Insufficient data for monthly implied futures at {timestamp} {ce_max_expiry} {pe_max_expiry}")

    def update_database(self) -> None:
        for _, row in self.df.iterrows():
            timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            weekly_value = row['implied_futures_weekly']
            monthly_value = row['implied_futures_monthly']
            sql = f"UPDATE {INSTRUMENT_NAME}_fut SET implied_futures_weekly = %s, implied_futures_monthly = %s WHERE timestamp = %s AND expiry = 'I'"
            values = (weekly_value, monthly_value, timestamp)

            self.cursor.execute(sql, values)
            self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def run(self):
        try:
            value = "false"
            print(f"value is {value}")
            self.df['implied_futures_weekly'] = np.nan
            self.df['implied_futures_monthly'] = np.nan
            ce, pe, fut_data = self.fetch_data()
            ce = ce.rename(columns ={0:'timestamp',1:'symbol', 2:'type', 3:'expiry', 4:'strike', 5:'close'})
            pe = pe.rename(columns ={0:'timestamp',1:'symbol', 2:'type', 3:'expiry', 4:'strike', 5:'close'})
            
            ce['strike']= ce['strike'].astype(int)
            pe['strike']= pe['strike'].astype(int)

            ce['expiry'] = pd.to_datetime(ce['expiry'])
            pe['expiry'] = pd.to_datetime(pe['expiry'])

            
            self.df = fut_data[[0, 1, 6]].copy()
            self.df.columns = ['timestamp', 'symbol', 'close']
            print(ce)
            print(pe)
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df.sort_values('timestamp', inplace=True)
            print(self.df)
            self.calculate_implied_futures(ce, pe)
            self.df = forward_fill_implied_futures(self.df, 'implied_futures_weekly')
            self.df = forward_fill_implied_futures(self.df, 'implied_futures_monthly')
            column_order = [
                    'timestamp', 'symbol', 'close', 'atm', 
                    'ce_symbol_weekly', 'ce_close_weekly', 'pe_symbol_weekly', 'pe_close_weekly',
                    'ce_symbol_monthly', 'ce_close_monthly', 'pe_symbol_monthly', 'pe_close_monthly',
                    'implied_futures_weekly', 'implied_futures_monthly'
                ]
            self.df = self.df[column_order]
            self.df.to_csv(f'{INSTRUMENT_NAME}_implied_futures.csv', index = False)
            print("file_saved")
            value="true"
            print(f"value is {value}")
            # self.update_database() # update the database with the implied futures
            self.close_connection() 
            return value
        except Exception as e:
            print(e)
            return "false"


'''
if __name__ == '__main__':
    print("calculating expiry data")
    calculate_and_save_expiry_data()
    print(f"calculating implied futures for {INSTRUMENT_NAME}")
    calculator = ImpliedFuturesCalculator()
    calculator.run()
'''
