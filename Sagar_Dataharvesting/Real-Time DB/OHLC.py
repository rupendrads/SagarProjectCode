from datetime import datetime
import mysql.connector
import pandas as pd

# Establish connection to MySQL database
mydb = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='root',
    database='sagar_dataharvesting',
    charset='utf8mb4',
)

# Fetch all distinct trading symbols
query_symbols = """
    SELECT DISTINCT Tradingsymbol
    FROM data_harvesting_20240705
"""
cursor = mydb.cursor()
cursor.execute(query_symbols)
symbols = cursor.fetchall()

# Create an empty DataFrame to store all OHLC data
all_ohlc_data = pd.DataFrame()

# Loop through each trading symbol and fetch OHLC data
for symbol in symbols:
    symbol = symbol[0]  # Extract the symbol string from the tuple

    # Fetch tick data for the current trading symbol
    query_data = f"""
        SELECT Tradingsymbol, LastUpdateTime, LastTradedPrice, LastTradedQuantity
        FROM data_harvesting_20240705
        WHERE Tradingsymbol = '{symbol}'
    """
    print(f'Symbol :{symbol}')
    cursor.execute(query_data)
    rows = cursor.fetchall()

    if not rows:
        continue  # Skip if no data is returned

    # Load data into a Pandas DataFrame
    tick_data = pd.DataFrame(rows, columns=['Tradingsymbol', 'LastUpdateTime', 'LastTradedPrice', 'LastTradedQuantity'])

    # Ensure the DataFrame is sorted by timestamp
    tick_data = tick_data.sort_values(by='LastUpdateTime')

    # Set the timestamp column as the index
    tick_data.set_index('LastUpdateTime', inplace=True)

    # Resample the data to 1-minute intervals and aggregate to OHLC
    ohlc_1min = tick_data['LastTradedPrice'].resample('1min').ohlc()

    # Resample the data to 1-minute intervals and sum the traded quantity
    quantity_1min = tick_data['LastTradedQuantity'].resample('1min').sum()

    # Combine OHLC data with quantity
    ohlc_1min['Volume'] = quantity_1min

    # Add the instrument name as a column
    ohlc_1min['Ticker'] = symbol

    # Reset index to turn the timestamp back into a column
    ohlc_1min.reset_index(inplace=True)

    # Split the 'LastUpdateTime' into 'Date' and 'Time' columns
    ohlc_1min['Date'] = ohlc_1min['LastUpdateTime'].dt.date
    ohlc_1min['Time'] = ohlc_1min['LastUpdateTime'].dt.time

    # Reorder columns to match the required format
    ohlc_1min = ohlc_1min[['Ticker', 'Date', 'Time', 'open', 'high', 'low', 'close', 'Volume']]

    # Append the data to the main DataFrame
    all_ohlc_data = pd.concat([all_ohlc_data, ohlc_1min])

# Close the cursor and connection
cursor.close()
mydb.close()

current_date = datetime.now().strftime('%Y%m%d')
csv_filename = f'all_symbols_1min_ohlc_{current_date}.csv'
# Save the concatenated DataFrame to a single CSV file
all_ohlc_data.to_csv(csv_filename, index=False)

# Display the DataFrame
print(all_ohlc_data.head())
