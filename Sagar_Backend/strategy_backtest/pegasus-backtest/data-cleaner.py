import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect(r'C:\Users\pegas\OneDrive\Desktop\clean data\marketdata.db')
cursor = conn.cursor()

# Find the next available index in the database
cursor.execute('SELECT MAX("index") FROM "nifty-24-new"')
next_index = cursor.fetchone()[0] + 1 if cursor.fetchone()[0] else 1

# Read data from CSV and insert into the table
with open('nifty_options_eg.csv', 'r') as file:
    # Create a CSV reader object
    csv_reader = csv.DictReader(file)
    # Iterate through each row in the CSV file
    for row in csv_reader:
        # Extract values from the dictionary
        date = row['date']
        symbol = row['symbol']
        open_price = float(row['open'])
        high = float(row['high'])
        low = float(row['low'])
        close = float(row['close'])
        volume = int(row['volume'])
        open_interest = int(row['openinterest'])
        options_type = row['options_type']
        strike = int(row['strike'])
        expiry_date = row['expiry_date']
        # Insert the row into the SQLite table with auto-incrementing index
        cursor.execute('INSERT INTO "nifty-24-new" ("index", "date", "symbol", "open", "high", "low", "close", "volume", "openinterest", "options_type", "strike", "expiry_date") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (next_index, date, symbol, open_price, high, low, close, volume, open_interest, options_type, strike, expiry_date))
        next_index += 1  # Increment index for the next row

# Commit the changes
conn.commit()

# Fetch and print the data from the table
cursor.execute('SELECT * FROM "nifty-24-new"')
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()
