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
    FROM data_harvesting_20240621 WHERE Tradingsymbol = 'NIFTY24JUNFUT' 
"""
cursor = mydb.cursor()
cursor.execute(query_symbols)
symbols = cursor.fetchall()

# Create an empty DataFrame to store all missing timestamps
all_missing_data = pd.DataFrame(columns=['Tradingsymbol', 'MissingTimestamp'])

# Loop through each trading symbol and fetch tick data
for symbol in symbols:
    symbol = symbol[0]  # Extract the symbol string from the tuple

    # Fetch tick data for the current trading symbol
    query_data = f"""
        SELECT Tradingsymbol, LastUpdateTime, LastTradedPrice, LastTradedQuantity
        FROM data_harvesting_20240621
        WHERE Tradingsymbol = '{symbol}'
    """
    cursor.execute(query_data)
    rows = cursor.fetchall()

    if not rows:
        continue  # Skip if no data is returned

    # Load data into a Pandas DataFrame
    tick_data = pd.DataFrame(rows, columns=['Tradingsymbol', 'LastUpdateTime', 'LastTradedPrice', 'LastTradedQuantity'])

    # Convert 'LastUpdateTime' to datetime format and set it as the index
    tick_data['LastUpdateTime'] = pd.to_datetime(tick_data['LastUpdateTime'])
    tick_data.set_index('LastUpdateTime', inplace=True)

    # Remove duplicate indices by aggregating (taking the last value for each second)
    tick_data = tick_data.groupby(tick_data.index).last()

    # Define the full range of timestamps at a second-level frequency
    full_range = pd.date_range(start=tick_data.index.min(), end=tick_data.index.max(), freq='s')

    # Reindex to this full range to find missing timestamps
    tick_data = tick_data.reindex(full_range)

    # Identify missing timestamps
    missing_timestamps = tick_data[tick_data.isnull().any(axis=1)].index

    # Create a DataFrame for missing timestamps
    missing_df = pd.DataFrame(missing_timestamps, columns=['MissingTimestamp'])
    missing_df['Tradingsymbol'] = symbol

    # Append to the main DataFrame
    all_missing_data = pd.concat([all_missing_data, missing_df], ignore_index=True)

# Close the cursor and connection
cursor.close()
mydb.close()

# Save all missing timestamps to a single CSV file
all_missing_data.to_csv('all_symbols_missing_timestamps.csv', index=False)

# Display the DataFrame
print(all_missing_data.head())
