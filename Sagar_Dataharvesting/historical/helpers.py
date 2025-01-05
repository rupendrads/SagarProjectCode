from datetime import datetime
from sqlalchemy import create_engine
import mysql.connector
from mysql.connector import Error

import mysql.connector
from datetime import datetime

def create_table():
    today_date = datetime.now().strftime("%d%m%Y")
    table_name = f"IEOD_{today_date}"

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pegasus",
            database="sagar_dataharvesting"
        )
        if connection.is_connected():
            cursor = connection.cursor()

            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone()
            if not table_exists:
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INT AUTO_INCREMENT,
                    timestamp DATETIME,
                    tradingsymbol VARCHAR(255),
                    open FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close FLOAT,
                    volume INT,
                    oi INT,
                    instrument_token INT,
                    segment VARCHAR(10),  # Additional column
                    PRIMARY KEY (id)
                );
                """
                cursor.execute(create_table_query)
                connection.commit()
                print(f"Table {table_name} created successfully.")
            else:
                print(f"Table {table_name} already exists.")
    finally:
        if connection.is_connected():
            connection.close()






def insert_dataframe_to_sql(df):
    today_date = datetime.now().strftime("%d%m%Y")
    table_name = f"ieod_{today_date}"

    # Database connection URI
    database_url = "mysql+mysqlconnector://root:pegasus@localhost/sagar_dataharvesting"
    
    engine = create_engine(database_url)

    # Insert data into the table
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

    print(f"Data successfully inserted into {table_name}")
class Logger:
    def __init__(self, filename):
        self.filename = filename
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{message} @ {timestamp}")
        with open(self.filename, "a") as log_file:
            log_file.write(f"{message} @ {timestamp}\n") 
            
def convert_datetime(start_time):
    current_time = datetime.now()
    combined_datetime = current_time.replace(hour=int(start_time.split(":")[0]), minute=int(start_time.split(":")[1]), second=0)

    formatted_datetime = combined_datetime.strftime("%b %d %Y %H%M%S")
    return formatted_datetime