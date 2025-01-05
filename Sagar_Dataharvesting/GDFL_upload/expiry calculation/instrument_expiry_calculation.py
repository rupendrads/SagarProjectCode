import pandas as pd
from collections import defaultdict
import logging
import mysql.connector
from expiry_constants import DBCONFIG, symbol, start_year, end_year, EXPIRY_TABLE_NAME
from datetime import datetime, timedelta

logging.basicConfig(filename='expiry_calculation.log', level=logging.INFO)

def fetch_data_from_db():
    connection = mysql.connector.connect(**DBCONFIG)
    cursor = connection.cursor()
    cursor.execute(f"USE {DBCONFIG['database']};")
    
    all_data = []
    for year in range(start_year, end_year + 1):
        print(year)
        query = f"""
        SELECT DATE(timestamp) as trading_day, expiry FROM {symbol}_{year}
        """
        print(query)
        df = pd.read_sql(query, connection)
        all_data.append(df)
    
    connection.close()
    return pd.concat(all_data, ignore_index=True)

def get_nearest_expiry(date, expiries):
    future_expiries = [exp for exp in expiries if exp >= date]
    return min(future_expiries) if future_expiries else None

def get_monthly_expiry(date, expiries):
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

trading_days = sorted(data['trading_day'].unique())
all_expiries = sorted(data['expiry'].unique())
result = pd.DataFrame(columns=['trading_day', 'current_expiry', 'monthly_expiry', 'symbol'])

for day in trading_days:
    current_expiry = get_nearest_expiry(day, all_expiries)
    monthly_expiry = get_monthly_expiry(day, all_expiries)

    result = result._append({
        'trading_day': day,
        'current_expiry': current_expiry if current_expiry else pd.NaT,
        'monthly_expiry': monthly_expiry if monthly_expiry else pd.NaT,
        'symbol': symbol
    }, ignore_index=True)

result['trading_day'] = result['trading_day'].dt.strftime('%Y-%m-%d')
result['current_expiry'] = result['current_expiry'].dt.strftime('%Y-%m-%d')
result['monthly_expiry'] = result['monthly_expiry'].dt.strftime('%Y-%m-%d')

connection = mysql.connector.connect(**DBCONFIG)
cursor = connection.cursor()
result.to_csv(f'{symbol}_expiry_data.csv', index=False)
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
print(insert_query)
data_to_insert = result.values.tolist()
cursor.executemany(insert_query, data_to_insert)

connection.commit()
cursor.close()
connection.close()

print(f"Daily expiry data saved to {symbol}_daily_expiry_data.csv")