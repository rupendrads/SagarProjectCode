import mysql.connector
import re
import time
from constants import db_creds

connection = mysql.connector.connect(
    host=db_creds['host'],
    user=db_creds['user'],
    password=db_creds['password'],
    database=db_creds['database']
)

try:
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    pattern = re.compile(r'.*_\d{4}$|.*_fut$')

    for (table_name,) in tables:
        if pattern.match(table_name):
            start_time = time.time()
            cursor.execute(f"OPTIMIZE TABLE {table_name}")
            cursor.fetchall()  
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Table '{table_name}' optimized in {elapsed_time:.4f} seconds.")

    connection.commit()
except mysql.connector.Error as error:
    print(f"Error optimizing tables: {error}")
finally:
    cursor.close()
    connection.close()
