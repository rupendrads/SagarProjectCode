# implied_futures_calculator.py
import mysql.connector
import pandas as pd
from datetime import datetime
from constants import *
from helpers import configure_logger, calculate_expiry_sets, forward_fill_implied_futures

class ImpliedFuturesCalculator:

    def __init__(self):
        self.logger = configure_logger(LOG_FILE_NAME)
        self.connection = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.connection.cursor()
        self.df = pd.DataFrame()
        self.start_year = int(START_DATE[:4])
        self.end_year = int(END_DATE[:4])
        print(self.start_year, self.end_year)
    def fetch_data(self):
        ce_data = pd.DataFrame()
        pe_data = pd.DataFrame()
        fut_data = pd.DataFrame()
 
        for year in range(self.start_year, self.end_year + 1):
            ce_table = f"{INSTRUMENT_NAME}_{year}"
            pe_table = f"{INSTRUMENT_NAME}_{year}"
            fut_table = f"{INSTRUMENT_NAME}_fut"

            # Adjust the query dates for the start and end of each year
            if year == self.start_year == self.end_year:
                # Both start and end dates are in the same year
                ce_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {ce_table} WHERE type='CE' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{END_DATE}'"
                pe_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {pe_table} WHERE type='PE' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{END_DATE}'"
                fut_query = f"SELECT timestamp, symbol, type, open, high, low, close FROM {fut_table} WHERE type='FUT' AND expiry ='I' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{END_DATE}'"
            elif year == self.start_year:
                # Start year condition (only filter on start date)
                year_end_date = f"{year}-12-31"
                ce_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {ce_table} WHERE type='CE' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{year_end_date}'"
                pe_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {pe_table} WHERE type='PE' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{year_end_date}'"
                fut_query = f"SELECT timestamp, symbol, type, open, high, low, close FROM {fut_table} WHERE type='FUT' AND expiry ='I' AND DATE(timestamp) BETWEEN '{START_DATE}' AND '{year_end_date}'"
            elif year == self.end_year:
                # End year condition (only filter on end date)
                year_start_date = f"{year}-01-01"
                ce_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {ce_table} WHERE type='CE' AND DATE(timestamp) BETWEEN '{year_start_date}' AND '{END_DATE}'"
                pe_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {pe_table} WHERE type='PE' AND DATE(timestamp) BETWEEN '{year_start_date}' AND '{END_DATE}'"
                fut_query = f"SELECT timestamp, symbol, type, open, high, low, close FROM {fut_table} WHERE type='FUT' AND expiry ='I' AND DATE(timestamp) BETWEEN '{year_start_date}' AND '{END_DATE}'"
            else:
                # Middle years (no specific filtering needed, fetch the entire year's data)
                ce_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {ce_table} WHERE type='CE'"
                pe_query = f"SELECT timestamp, symbol, type, expiry, strike, close FROM {pe_table} WHERE type='PE'"
                fut_query = f"SELECT timestamp, symbol, type, open, high, low, close FROM {fut_table} WHERE type='FUT' AND expiry ='I'"

            print(ce_query)
            print(pe_query)
            print(fut_query)
            self.cursor.execute(ce_query)
            ce_data = pd.concat([ce_data, pd.DataFrame(self.cursor.fetchall())], ignore_index=True)
            self.cursor.execute(pe_query)
            pe_data = pd.concat([pe_data, pd.DataFrame(self.cursor.fetchall())], ignore_index=True)
            self.cursor.execute(fut_query)
            fut_data = pd.concat([fut_data, pd.DataFrame(self.cursor.fetchall())], ignore_index=True)

        return ce_data, pe_data, fut_data


    def calculate_implied_futures(self, ce_data, pe_data):
        self.df['atm'] = (round(self.df['close'] / STRIKE_DIFFERENCE) * STRIKE_DIFFERENCE).astype(int)

        for idx, row in self.df.iterrows():
            timestamp = row['timestamp']
            atm = row['atm']

            ce_data_filtered = ce_data[(ce_data['timestamp'] == timestamp) & (ce_data['strike'] == atm)]
            pe_data_filtered = pe_data[(pe_data['timestamp'] == timestamp) & (pe_data['strike'] == atm)]

            try:
                ce_min_expiry = min(ce_data_filtered['expiry'])
                pe_min_expiry = min(pe_data_filtered['expiry'])
                
                self.calculate_implied_futures_weekly(ce_min_expiry, pe_min_expiry, ce_data_filtered, pe_data_filtered, idx, atm, timestamp)
            except Exception as e:
                self.logger.error(f"Error processing weekly implied futures at {timestamp}: {e}")

            try:
                max_expiry_ce, max_expiry_pe = calculate_expiry_sets(ce_data_filtered, pe_data_filtered, timestamp)
                if max_expiry_ce and max_expiry_pe:
                    self.calculate_implied_futures_monthly(max_expiry_ce, max_expiry_pe, ce_data_filtered, pe_data_filtered, idx, atm, timestamp)
                else:
                    self.logger.warning(f"Invalid monthly expiries at {timestamp}")
            except Exception as e:
                self.logger.error(f"Error processing monthly implied futures at {timestamp}: {e}")

    def calculate_implied_futures_weekly(self, ce_min_expiry, pe_min_expiry, ce_data_filtered, pe_data_filtered, idx, atm, timestamp):
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

    def calculate_implied_futures_monthly(self, ce_max_expiry, pe_max_expiry, ce_data_filtered, pe_data_filtered, idx, atm, timestamp):
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

    def update_database(self):
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
        ce, pe, fut_data = self.fetch_data()
        ce = ce.rename(columns ={0:'timestamp',1:'symbol', 2:'type', 3:'expiry', 4:'strike', 5:'close'})
        pe = pe.rename(columns ={0:'timestamp',1:'symbol', 2:'type', 3:'expiry', 4:'strike', 5:'close'})
        
        ce['strike']= ce['strike'].astype(int)
        pe['strike']= pe['strike'].astype(int)

        ce['expiry'] = pd.to_datetime(ce['expiry'])
        pe['expiry'] = pd.to_datetime(pe['expiry'])

        
        print("data fetched")
        self.df = fut_data[[0, 1, 6]].copy()
        self.df.columns = ['timestamp', 'symbol', 'close']
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df.sort_values('timestamp', inplace=True)
        print("implied futures calculation")
        self.calculate_implied_futures(ce, pe)
        print("calculation done")
        # forward_fill_implied_futures(self.df, 'implied_futures_weekly')
        # forward_fill_implied_futures(self.df, 'implied_futures_monthly')
        self.df.to_csv('implied_futures.csv', index = False)
        print(self.df)
        print("file_saved")
        # self.update_database()
        # self.close_connection()

if __name__ == '__main__':
    calculator = ImpliedFuturesCalculator()
    calculator.run()
