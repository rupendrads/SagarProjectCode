# -- SELECT COUNT(DISTINCT(LastUpdateTime)) FROM sagar_dataharvesting.data_harvesting_20241127 where Tradingsymbol = 'BANKNIFTY24NOVFUT'

import pandas as pd
import mysql.connector
config = {
    "user": "root",
    "password": "root",
    "host" : "localhost",
    "database": "sagar_dataharvesting"
}

query = '''
SELECT DISTINCT(LastUpdateTime)
FROM data_harvesting_20241127
WHERE tradingsymbol = 'BANKNIFTY24NOVFUT'
'''

connection = mysql.connector.connect(**config)
cursor = connection.cursor()
cursor.execute(query)
data = cursor.fetchall()
df = pd.DataFrame(data, columns =['datetimestamp'])

df.to_csv("novdata.csv", index=False)
