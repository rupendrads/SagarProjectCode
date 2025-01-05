#import mysql.connector
#from mysql.connector import Error
import datetime
from sqlalchemy import create_engine

'''
def create_table():
    # Get current date in DDMMYYYY format
    today_date = datetime.datetime.now().strftime("%d%m%Y")
    table_name = f"IEOD_{today_date}"

    try:
        # Connection configuration
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="ifl"
        )
        if connection.is_connected():
            cursor = connection.cursor()

            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone()
            # SQL query to create the table if it does not exist
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
                    PRIMARY KEY (id)
                );
                """

            # Execute the query
                cursor.execute(create_table_query)
                connection.commit()
                print(f"Table {table_name} created successfully.")
            else:
                print(f"Table {table_name} already exists.")

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

create_table()



def insert_dataframe_to_sql(df):
    today_date = datetime.datetime.now().strftime("%d%m%Y")
    table_name = f"ieod_{today_date}"

    # Database connection URI
    database_url = "mysql+mysqlconnector://root:root@localhost/ifl"
    
    engine = create_engine(database_url)

    # Insert data into the table
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

    print(f"Data successfully inserted into {table_name}")
'''