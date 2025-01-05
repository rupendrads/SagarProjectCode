from aifc import Error
import asyncio
from multiprocessing import pool

import socketio.client
import aiomysql # type: ignore
import pandas as pd
import requests
import json
from async_market import MDSocket_io, MDSocketManager
import logging
import urllib3
from datetime import datetime, timedelta
from broker import XTSlogin
import mysql.connector
from queue import Queue, Empty  
import threading
from helpers import Logger, broker_login, isLatestInstrumentFiles, load_config 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import mysql.connector.pooling
import socketio
sio = socketio.client


buffer = []
BULK_INSERT_SIZE = 1  # Number of records to insert in bulk
MAX_RETRIES = 3  # Maximum number of retries for database connection
INITIAL_BULK_INSERT_SIZE = 10  # Initial number of records to insert in bulk

DB_CONNECTION_PARAMS = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pegasus',
    'db': 'sagar_dataharvesting',
    'port': 3306
}
time_difference = 0
config = load_config('config.json')
if config["timezone"].lower()=="uk":
    time_difference = 60
else:
    time_difference= 330
#print(time_difference)
if config["root_flag"] == "live":
    creds = load_config('secret.json')
    root_url = config["live_url"]
else:
    creds = load_config('sandbox.json')
    root_url = config["sandbox_url"]

xts = XTSlogin(root_url)
logger = Logger("trade.txt")

headers = {
    "Content-Type": "application/json"
}

async def on_disconnect():
    print("Disconnected from server")

async def on_connect():
    """Connect from the socket."""
    print('Market Data Socket connected successfully!')
    logger.log('symbols subscribed')

async def connect_with_retries(loop, retries=MAX_RETRIES):
    print(f'connect_with_retries')
    for attempt in range(retries):
        try:
            pool = await aiomysql.create_pool(**DB_CONNECTION_PARAMS, loop=loop)
            return pool
        except Error as e:
            print(f"Database connection error: {e}")
            if attempt < retries - 1:
                print('Rupendra Sleep')
                await asyncio.sleep(5)  # Wait before retrying
            else:
                raise e

def get_token_name(token_id, token_tuple):
    #print(f'get_token_name')
    token_dict = token_tuple[0]  # Access the dictionary inside the tuple
    return token_dict.get(token_id, "Token ID not found")

async def insert_trade_data(data,combined_token_names):
    try:
        # Establish the database connection
        #print(f'combined_token_names :{combined_token_names}')
        connection = mysql.connector.connect(
           **DB_CONNECTION_PARAMS
        )
        table_namenew = "data_harvesting" + "_" + datetime.now().strftime("%Y%m%d")
        exchange_id = data.get('ExchangeInstrumentID')
        token_name = None

        time_difference = 0
        config = load_config('config.json')
        if config["timezone"].lower()=="uk":
            time_difference = 60
        else:
            time_difference= 330
    
        if isinstance(combined_token_names, dict):
            token_name = combined_token_names.get(exchange_id, None)
        elif isinstance(combined_token_names, list):
            token_name = next((item for item in combined_token_names if item.get('ExchangeInstrumentID') == exchange_id), None)
       
        if connection.is_connected():
            cursor = connection.cursor()
            
            # SQL insert statement
            insert_query = f"""INSERT INTO {table_namenew} (
                MessageCode, 
                ExchangeSegment, 
                ExchangeInstrumentID, 
                BookType, 
                XMarketType, 
                LastTradedPrice, 
                LastTradedQuantity, 
                LastUpdateTime,
                PercentChange, 
                Close,
                Tradingsymbol,
                OverallData
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            # Prepare the data as a tuple
            record = (
                data['MessageCode'],               
                data['ExchangeSegment'],
                data['ExchangeInstrumentID'],
                data['BookType'],
                data['XMarketType'],
                data['LastTradedPrice'],
                data['LastTradedQunatity'],
                datetime.fromtimestamp(data['LastUpdateTime'] + 315532800) - timedelta(minutes=time_difference) if data['LastUpdateTime'] is not None else None,
                data['PercentChange'],
                data['Close'],
                get_token_name(exchange_id, combined_token_names),
                json.dumps(data)  # Ensure item is a dictionary or JSON-serializable object
            )
            
            # Execute the insert statement
            cursor.execute(insert_query, record)
            
            # Commit the transaction
            connection.commit()
       
    except mysql.connector.Error as error:
        print(f"Failed to insert record: {error}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            #print("MySQL connection is closed")


async def insert_data_queue(data_queue,  combined_token_names):
    
    for _ in range(BULK_INSERT_SIZE):
        try:            
            result = data_queue.get()     
            data = json.loads(result)
       
            await insert_trade_data(data, combined_token_names)
        except Empty:
            print('Queue is empty or timeout occurred') 

    current_time = datetime.now()

    # Extract hour and minute from the end_time string
    end_time_str = config['end_time']
    end_hour, end_minute = map(int, end_time_str.split(':'))

    # Replace hour and minute in the current datetime object
    end_time = current_time.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)

    # Insert all data in table after market hours
    if current_time > end_time:
        while not data_queue.empty():
            try:
                result = data_queue.get(timeout=1)  # Add a timeout to avoid blocking indefinitely
                data = json.loads(result)
                await insert_trade_data(data, combined_token_names)
            except Empty:
                print('Queue is empty or timeout occurred')
            break

      
def load_holidays(filename):
    print(f'load_holidays')
    holidays = []
    with open(filename, 'r') as f:
        for line in f:
            holidays.append(datetime.strptime(line.strip(), "%Y-%m-%d").date())
    return holidays

def table_exists(table_name, mycursor):
    """Checks if the table exists in the database."""
    print(f'table_exists')
    mycursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return mycursor.fetchone() is not None

async def create_table_if_not_exists(table_name, pool):
    """Creates the data table if it does not exist."""
    print(f'create_table_if_not_exists')
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Check if the table already exists
            await cur.execute(f"SHOW TABLES LIKE '{table_name}'")
            if await cur.fetchone() is not None:
                print(f"Table '{table_name}' already exists.")
                return
            else:
                if config["timezone"].lower()=="uk":
                    create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        MessageCode INT,
                        ExchangeSegment INT,
                        ExchangeInstrumentID INT,
                        BookType INT,
                        XMarketType INT,
                        LastTradedPrice FLOAT,
                        LastTradedQuantity INT,
                        LastUpdateTime DATETIME,
                        Close FLOAT,
                        Tradingsymbol VARCHAR(255),
                        PercentChange DECIMAL(10, 9),
                        OverallData TEXT,
                        CreatedAt DATETIME DEFAULT (CURRENT_TIMESTAMP + INTERVAL 4 HOUR + INTERVAL 30 MINUTE),
                        INDEX idx_id (id),
                        INDEX idx_last_traded_price (LastTradedPrice),
                        INDEX `idx_tradingsymbol` (`Tradingsymbol`),
                        INDEX `idx_exchange_instrument_id` (`ExchangeInstrumentID`)                    
                    )
                    """
                else:
                    create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        MessageCode INT,
                        ExchangeSegment INT,
                        ExchangeInstrumentID INT,
                        BookType INT,
                        XMarketType INT,
                        LastTradedPrice FLOAT,
                        LastTradedQuantity INT,
                        LastUpdateTime DATETIME,
                        Close FLOAT,
                        Tradingsymbol VARCHAR(255),
                        PercentChange DECIMAL(10, 9),
                        OverallData TEXT,
                        CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_id (id),
                        INDEX idx_last_traded_price (LastTradedPrice),
                        INDEX `idx_tradingsymbol` (`Tradingsymbol`),
                        INDEX `idx_exchange_instrument_id` (`ExchangeInstrumentID`)                    
                    )
                    """
                await cur.execute(create_table_query)
                print(f"Table '{table_name}' created successfully or already exists.")

async def main():
    print(f'Main')
    global data_queue
    data_queue = asyncio.Queue()
    #Load NSE holidays
    # holidays = load_holidays('nse_holidays.txt')
    # today = datetime.today().date()

    # # # Check if today is Saturday, Sunday, or an NSE holiday
    # if today.weekday() >= 5 or today in holidays:
    #     print("Today is a weekend or an NSE holiday. Exiting.")
    #     return

    start_time = config['start_time']
    end_time = config['end_time']
    app_key = creds['app_key']
    secret_key = creds['secret_key']
    port = root_url
    table_name = "data_harvesting" + "_" + datetime.now().strftime("%Y%m%d")

    loop = asyncio.get_event_loop()
    pool = await connect_with_retries(loop)

    await create_table_if_not_exists(table_name, pool)

    market_token, userid = broker_login(xts, creds)
    xts.market_token, xts.userid = market_token, userid

    if not isLatestInstrumentFiles():
        xts.update_master_db()
    else:
        print("Already updated nfo and nsecm files")

    data_queue = Queue()

    fut = pd.read_csv('nfo.csv', low_memory=False)
    index_options = fut[(fut.Series == 'OPTIDX') & (fut["Name"].isin(["NIFTY"])) & (fut["UnderlyingIndexName"].isin(["Nifty 50"]))]
    index_options = index_options[index_options.ContractExpiration == min(index_options.ContractExpiration)]
    index_options = index_options.set_index('ExchangeInstrumentID')['Description'].to_dict()
    # print(index_options)
    index_futures = fut[(fut.Series == 'FUTIDX')]
    index_futures = fut[(fut.Series == 'FUTIDX') & (fut["Name"].isin(["NIFTY", "BANKNIFTY"])) & (fut["UnderlyingIndexName"].isin(["Nifty 50", "Nifty Bank"])) ]
    index_futures = index_futures.sort_values(by='ContractExpiration')
    index_futures = index_futures.head(2)
    futures_list = list(set(index_futures['Name']))
    # print(index_futures)
    fut_instrument_ids = []
    for idx in futures_list:
        futures = index_futures[index_futures['Name'] == idx]
        current_expiry = futures.ContractExpiration.min()
        futures = futures[(futures['ContractExpiration'] == current_expiry) & (~pd.isna(futures['UnderlyingIndexName']))]
        fut_instrument_ids.append(futures['ExchangeInstrumentID'].values[0].item())
    # print(fut_instrument_ids)
    stk_index_futures = fut[fut.Series == 'FUTSTK']
    stk_futures_list = list(set(stk_index_futures['Name']))
    futures_list = index_futures.set_index('ExchangeInstrumentID')['Description'].to_dict()
    subscribed_symbol = []
    # print(fut_instrument_ids)
    for option in fut_instrument_ids:
        data = {'exchangeInstrumentID': option, 'exchangeSegment': 2}
        subscribed_symbol.append(data)
    for id, name in index_options.items():
        data = {'exchangeInstrumentID': id, 'exchangeSegment': 2}
        subscribed_symbol.append(data)
    subscribed_symbol.append({'exchangeInstrumentID': 26000, 'exchangeSegment': 1})
    subscribed_symbol.append({'exchangeInstrumentID': 26001, 'exchangeSegment': 1})

    current_time = datetime.now()
    combined_token_names = futures_list 
    combined_token_names.update(index_options)
    combined_token_names[26000] = 'NIFTY 50'
    combined_token_names[26001] = 'NIFTY BANK'
    
    #combined_token_names ={26000 : 'NIFTY 50'}
    #subscribed_symbol =[{'exchangeSegment': 1, 'exchangeInstrumentID': 26000}]
    print(combined_token_names)
    # start_time = current_time.replace(hour=int(start_time.split(':')[0]), minute=int(start_time.split(':')[1]), second=0, microsecond=0)
    # end_time = current_time.replace(hour=int(end_time.split(':')[0]), minute=int(end_time.split(':')[1]), second=0, microsecond=0)
    # if current_time < start_time:
    #     time_gap = (start_time - current_time).total_seconds()
    #     print(f"Sleeping for {time_gap} seconds.")
    #     #time.sleep(time_gap)
    # print(f"market token is {market_token}")
    # # xts.subscribe_symbols(subscribed_symbol, market_token)
    # # soc = MDSocket_io(token=market_token, port=port, userID=userid, queue=data_queue, combined_token_names=combined_token_names)

    # # soc.on_connect = on_connect
    # # el = soc.get_emitter()
    # # el.on('connect', soc.on_connect)
    # # el.on('1512-json-full', soc.on_message1512_json_full)

    # # soc.on_message1512_json_full('1512-json-full')
    # # await soc.connect()
    # print(subscribed_symbol)
    soc = MDSocketManager(
            socket_count=1,  # Number of WebSocket connections to use
            token=market_token,
            userID=userid,
            port=port,
            queue=Queue(),
            combined_token_name=combined_token_names,
            xts = xts,
            symbols=subscribed_symbol
    )
    await soc.start_all()
     
if __name__ == "__main__":
    print(f'Main')
    asyncio.run(main())
