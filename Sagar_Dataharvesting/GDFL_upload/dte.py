import pandas as pd
import mysql.connector
import glob
from constants import DB_CONFIG

def calculate_dte(symbol):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT trading_day FROM trading_days ORDER BY trading_day")
    trading_days = [row[0] for row in cursor.fetchall()]
    trading_days = pd.to_datetime(trading_days)

    def trading_days_between(start_date, end_date):
        return len(trading_days[(trading_days > start_date) & (trading_days <= end_date)])
 
    all_dfs = []

    import re

    for file_path in glob.glob(f'{symbol}_expiry_data_????.csv'):
        if re.search(f'{symbol}_expiry_data_\\d{{4}}\\.csv$', file_path):
            df = pd.read_csv(file_path)
            df['trading_day'] = pd.to_datetime(df['trading_day'])
            df['current_expiry'] = pd.to_datetime(df['current_expiry'])
            df['monthly_expiry'] = pd.to_datetime(df['monthly_expiry'])

            df['DTE_current'] = df.apply(lambda row: trading_days_between(row['trading_day'], row['current_expiry']), axis=1)
            df['DTE_monthly'] = df.apply(lambda row: trading_days_between(row['trading_day'], row['monthly_expiry']), axis=1)

            all_dfs.append(df)

            print(f"DTE calculation completed for {symbol} in file {file_path}")

    if not all_dfs:
        print(f"No matching files found for symbol {symbol}")
        return

    combined_df = pd.concat(all_dfs, ignore_index=True)

    combined_df = combined_df.sort_values('trading_day')

    output_file = f'{symbol}_DTE.csv'
    combined_df.to_csv(output_file, index=False)
    print(f"Results for {symbol} saved to {output_file}")

    cursor.close()
    conn.close()

    print(f"DTE calculation completed and saved for {symbol}.")
symbol='nifty'
calculate_dte(symbol)
