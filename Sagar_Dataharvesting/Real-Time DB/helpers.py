from datetime import datetime
from sqlalchemy import create_engine
import mysql.connector
from mysql.connector import Error
import os
import json

def load_config(filename):
     with open(filename, 'r') as f:
         return json.load(f)
     
def isLatestInstrumentFiles():
    # Define the filenames to check
    file_names = ['nfo.csv', 'nsecm.csv']
    
    # Today's date
    today = datetime.now().date()
    folder_path = os.getcwd()
    for file_name in file_names:
        # Construct full file path
        file_path = os.path.join(folder_path, file_name)
        
        if os.path.exists(file_path):
            modification_time = os.path.getmtime(file_path)
            file_mod_date = datetime.fromtimestamp(modification_time).date()
            
            if file_mod_date != today:
                print(f"{file_name} was not modified today.")
                return False
            else:
                pass
        else:
            return False
    return True



def broker_login(xts, creds):
    tokens_file = 'tokens.json'
    
    if os.path.exists(tokens_file):
        with open(tokens_file, 'r') as file:
            data = json.load(file)
        
        last_date = datetime.strptime(data['date'], '%Y-%m-%d')
        if last_date.date() == datetime.now().date():
            market_token = data['market_token']
            # interactive_token = data['interactive_token']
            userid = data['userid']
            print("Using stored tokens.")
            return market_token, userid
    market_token, userid = xts.market_login(creds['secret_key'], creds['app_key'])
    with open(tokens_file, 'w') as file:
        json.dump({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'market_token': market_token,
            'userid': userid
        }, file)
    print("Stored new tokens.")
    
    return market_token, userid
def create_table():
    # Get current date in DDMMYYYY format
    today_date = datetime.now().strftime("%d%m%Y")
    table_name = f"IEOD_{today_date}"

    try:
        # Connection configuration
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
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        self.filename = f'{filename}-{self.current_date}.txt'
    
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