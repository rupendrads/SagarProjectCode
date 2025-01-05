import pandas as pd
import mysql.connector

# Connect to the database
cnx = mysql.connector.connect(user='root', password='root',
                              host='localhost', database='sagar_dataharvesting')
query = "SELECT id,MessageCode,ExchangeSegment,ExchangeInstrumentID,BookType,XMarketType,LastTradedPrice,LastTradedQuantity,close,Tradingsymbol,LastUpdateTime FROM sagar_dataharvesting.data_harvesting_20240621  where Tradingsymbol = 'NIFTY24JUNFUT' order by 1"

# Execute the query and fetch the data into a DataFrame
df = pd.read_sql(query, cnx)

# Export the DataFrame to a CSV file
df.to_csv('D:\\file.csv', index=False)

# Close the connection
cnx.close()