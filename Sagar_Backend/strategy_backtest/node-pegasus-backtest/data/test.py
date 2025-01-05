import pandas as pd
import mysql.connector
path = 'C:\Users\pegas\OneDrive\Desktop\indexing\weekly_expiry_options_2020.csv'
print(path)
df = pd.read_csv('weekly_expiry_options_2020.csv')[['day','expiry']]
df['day'] = pd.to_datetime(df['day'])
df['expiry'] = pd.to_datetime(df['expiry'])

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pegasus',
    'database' : 'index_data'
}
conn = mysql.connector.connect(**db_config)

cursor = conn.cursor()

for index, row in df.iterrows():
    day = row['day']
    expiry = row['expiry']
    print(day)
    query = f"SELECT * FROM NIFTY_2020 WHERE DATE(timestamp) = '{day}'"
    cursor.execute(query)
    result = cursor.fetchall()
    print(result)

cursor.close()
conn.close()
