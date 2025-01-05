import pandas as pd
from datetime import datetime

class DataCleaner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def clean_data(self):
        # Read the CSV file
        self.data = pd.read_csv(self.file_path)

        # Rename the 'Ticker' column to 'symbol'
        self.data.rename(columns={'Ticker': 'symbol'}, inplace=True)

        # Convert 'Time' to datetime and create 'datetime' column
        self.data['Time'] = pd.to_datetime(self.data['Time'])
        self.data['Time'] = self.data['Time'].dt.time
        self.data['datetime'] = pd.to_datetime(self.data['Date']) + pd.to_timedelta(self.data['Time'].astype(str))

        # Lowercase column names
        self.data.columns = self.data.columns.str.lower()

        # Drop 'Date' and 'Time' columns
        self.data.drop(['date', 'time'], axis=1, inplace=True)

        # Floor 'datetime' column to minutes
        self.data['datetime'] = self.data['datetime'].dt.floor('min')

        # Move 'datetime' column to the first position
        datetime_column = self.data.pop('datetime')
        self.data.insert(0, 'date', datetime_column)

        # Extract 'options_type' and 'strike' from 'symbol'
        self.data['options_type'] = self.data['symbol'].str.replace('.NFO', '').str[-2:]
        self.data['options_type'] = self.data['options_type'].apply(lambda x: 'FUT' if x not in ['PE', 'CE'] else x)
        self.data['strike'] = self.data['symbol'].str.replace('.NFO', '').str[-7:-2]
        self.data['strike'] = self.data['strike'].apply(lambda x: x if x.isdigit() else None)
        
    def get_clean_data(self):
        return self.data

    def save_clean_data(self, output_file):
        self.data.to_csv(output_file, index=False)

    def save_clean_data_by_symbol(self, symbol):
        # Filter data for the specified symbol
        symbol_data = self.data[self.data['symbol'].str.contains(r'\b{}\b'.format(symbol), case=False)]
        # symbol_data = symbol_data[symbol_data['options_type']!='FUT']
        # Get today's date in YYYYMMDD format
        today_date = datetime.today().strftime('%Y%m%d')

        # Generate file name with symbol and today's date
        file_name = f"{symbol}_{today_date}.csv"
        # Save the filtered data to a CSV file
        symbol_data.to_csv(file_name, index=False)

# Example usage:
if __name__ == "__main__":
    cleaner = DataCleaner(r'C:\Users\pegas\OneDrive\Desktop\data\2024\jan\GFDLNFO_BACKADJUSTED_02012024.csv')
    cleaner.clean_data()

    # Save separate files for NIFTY, BANKNIFTY, MIDCAPNIFTY, and FINNIFTY
    cleaner.save_clean_data_by_symbol('NIFTY')
    cleaner.save_clean_data_by_symbol('BANKNIFTY')
    cleaner.save_clean_data_by_symbol('MIDCAPNIFTY')
    cleaner.save_clean_data_by_symbol('FINNIFTY')
