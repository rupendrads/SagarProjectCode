import mysql.connector
import pandas as pd
from datetime import datetime


try:
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current script
    sagar_common_path = os.path.join(current_dir, "../../Sagar_common")  # Go up two levels to "OGCODE"
    if sagar_common_path not in sys.path:
        sys.path.append(sagar_common_path)
    from common_function import fetch_parameter
except ImportError as e:
    print(f"Errorfetching db details: {e}")

#from constants import *

env = "dev"  # Environment, e.g., 'dev', 'prod'
key = "db_index_data"  # Example key
db_config = fetch_parameter(env, key)
if db_config is None:
    raise HTTPException(status_code=500, detail="Failed to fetch database configuration.")
print(f"Fetched db config: {db_Value}")
db_config["database"] = db_name


connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()
cursor.execute(f"SELECT timestamp,symbol,type,open,high,low,close FROM symbol WHERE type='FUT' AND symbol={instrument_expiry_symbol} ")
rows = cursor.fetchall()
fut = pd.DataFrame(rows)
query =f'''  SELECT *
            FROM {instrument_table_name}
            WHERE DATE(timestamp) BETWEEN {start_date} AND {end_date};
'''

cursor.execute(f"SELECT timestamp,symbol,type,expiry, strike,close FROM {instrument_table_name} WHERE type='CE'")
rows = cursor.fetchall()
ce = pd.DataFrame(rows)
cursor.execute(f"SELECT timestamp,symbol,type,expiry, strike,close FROM {instrument_table_name} WHERE type='PE'")
rows = cursor.fetchall()
pe = pd.DataFrame(rows)

ce = ce.rename(columns ={0:'timestamp',1:'symbol', 2:'type', 3:'expiry', 4:'strike', 5:'close'})
pe = pe.rename(columns ={0:'timestamp',1:'symbol', 2:'type', 3:'expiry', 4:'strike', 5:'close'})

df = fut[[0,1,6]].copy()
df = df.rename(columns = {0:'timestamp', 1:'symbol', 6:'close'})
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.sort_values('timestamp', inplace=True)
df.reset_index(inplace=True, drop=True)
ce['strike']= ce['strike'].astype(int)
pe['strike']= pe['strike'].astype(int)
ce['expiry'] = pd.to_datetime(ce['expiry'])
pe['expiry'] = pd.to_datetime(pe['expiry'])
df['atm'] = (round(df['close'] / 50) * 50)
df['atm'] = df['atm'].astype(int)

counter = 0
anti_counter = 0
for idx, row in df.iterrows():
    try:
        timestamp = row['timestamp']
        atm = row['atm']
        
        ce_data = ce[(ce['timestamp'] == timestamp) & (ce['strike'] == atm)]
        pe_data = pe[(pe['timestamp'] == timestamp) & (pe['strike'] == atm)]

        ce_min_expiry = min(ce_data['expiry'])
        pe_min_expiry = min(pe_data['expiry'])
        ce_max_expiry = max(ce_data['expiry'])
        pe_max_expiry = max(pe_data['expiry'])
        
        ce_symbol_min = ce_data[ce_data['expiry'] == ce_min_expiry]['symbol'].values[0]
        pe_symbol_min = pe_data[pe_data['expiry'] == pe_min_expiry]['symbol'].values[0]
        ce_symbol_max = ce_data[ce_data['expiry'] == ce_max_expiry]['symbol'].values[0]
        pe_symbol_max = pe_data[pe_data['expiry'] == pe_max_expiry]['symbol'].values[0]

        ce_close_min = ce_data[ce_data['expiry'] == ce_min_expiry]['close'].values[0]
        pe_close_min = pe_data[pe_data['expiry'] == pe_min_expiry]['close'].values[0]
        ce_close_max = ce_data[ce_data['expiry'] == ce_max_expiry]['close'].values[0]
        pe_close_max = pe_data[pe_data['expiry'] == pe_max_expiry]['close'].values[0]
        
        implied_futures_weekly = round((atm + ce_close_min - pe_close_min), 2)
        implied_futures_monthly = round((atm + ce_close_max - pe_close_max), 2)
        df.loc[idx, 'implied_futures_weekly'] = implied_futures_weekly
        df.loc[idx, 'implied_futures_monthly'] = implied_futures_monthly
        
        counter+=1
    except Exception  as e:
        anti_counter+=1
        print(f'number of rows failed to derive Implied futures {anti_counter}')
        print(f"Error processing data at timestamp: {timestamp}. Error: {e}")

for index, row in df.iterrows():
    timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S') 
    weekly_value = row['implied_futures_weekly']
    monthly_value = row['implied_futures_monthly']
    
    sql = f"UPDATE {symbol} SET implied_futures_weekly = %s, implied_futures_monthly = %s WHERE timestamp = %s AND symbol = {instrument_expiry_symbol}"
    print(sql)
    values = (weekly_value, monthly_value, timestamp)
    
    cursor = connection.cursor()
    cursor.execute(sql, values)
    connection.commit()
    cursor.close()
print("updated")
connection.close()