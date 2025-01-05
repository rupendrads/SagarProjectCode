from aifc import Error
import asyncio
from multiprocessing import pool

import socketio.client
import aiomysql # type: ignore
import pandas as pd
import requests
import json
from async_marketOriginal import MDSocket_io
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
BULK_INSERT_SIZE = 100  # Number of records to insert in bulk
MAX_RETRIES = 3  # Maximum number of retries for database connection
INITIAL_BULK_INSERT_SIZE = 10  # Initial number of records to insert in bulk

DB_CONNECTION_PARAMS = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'db': 'sagar_dataharvesting',
    'port': 3306
}

config = load_config('config.json')
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

async def bulk_insert_to_db(buffer, table_name, combined_token_names, pool):
    #print(f'inside bulk_insert_to_db ')
    """Performs bulk insert of data into the database."""
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                query = f"""
                INSERT INTO {table_name} (
                    MessageCode, ExchangeSegment, ExchangeInstrumentID, BookType, XMarketType, 
                    LastTradedPrice, LastTradedQuantity, LastUpdateTime, Close, Tradingsymbol, OverallData
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = [
                    (
                        item.get("MessageCode", None),
                        item.get("ExchangeSegment", None),
                        item.get("ExchangeInstrumentID", None),
                        item.get("BookType", None),
                        item.get("XMarketType", None),
                        item.get("LastTradedPrice", None),
                        item.get("LastTradedQunatity", None),
                        datetime.fromtimestamp(item.get("LastUpdateTime", None) + 315532800) - timedelta(minutes=60) if item.get("LastUpdateTime", None) is not None else None,
                        item.get("Close", None),
                        combined_token_names.get(item.get("ExchangeInstrumentID", None), None),
                        json.dumps(item)  # Ensure item is a dictionary or JSON-serializable object
                    )
                    for item in buffer
                ] 
                print(values)          
                #print(values)
                await cur.executemany(query, values)
                await conn.commit()
            except Exception as e:
                logger.log(f"Error during bulk insert: {e}")
                await conn.rollback()

async def get_data_queue(data_queue, table_name, end_time, combined_token_names, pool, soc, subscribed_symbol, market_token):
    #print(f'Called get_data_queue {data_queue.qsize()}')
    buffer = []
    global BULK_INSERT_SIZE
    processed_items = []
        
    while True:
        if datetime.now() >= end_time:
            logger.log('Time is over, exiting')
            await soc.disconnect()
            break
        results = []

        if  not data_queue.empty() and  data_queue.qsize() > BULK_INSERT_SIZE:            
            try:    
                for _ in range(BULK_INSERT_SIZE):
                    try:
                        result = await asyncio.get_event_loop().run_in_executor(None, data_queue.get, True, 1)  # Non-blocking with timeout
                        results.append(result)
                    except Empty:
                        print('Queue is empty or timeout occurred')               
            except Empty:
                logger.log('Queue is empty')
                continue
            except json.JSONDecodeError as e:
                logger.log(f'JSON decoding error: {e}')
                continue
            except Exception as e:
                logger.log(f'Unexpected error: {e}')
                continue            
            
            #print(f'results {len(results)}')
            for result in results:
                result_json = json.dumps(result) #Point to check tommorow
                buffer.append(result_json)
                processed_items.append(results)  
            try:
                #print(f'len(buffer  :{len(buffer)}')
                parsed_data = parse_json_strings(buffer)
                #logger.log(f'parsed_data {parsed_data}')
                await bulk_insert_to_db(parsed_data, table_name, combined_token_names, pool)
                buffer = []  # Clear the buffer after successful insert
                
                # Mark the items as done after successful insert
                for raw_data in processed_items:
                    #print('task_done')
                    data_queue.task_done()

                processed_items = []

            except Exception as e:
                logger.log(f"Error during bulk insert: {e}")
                for item in processed_items:
                        data_queue.put(item)
                processed_items = []
            
def parse_json_strings(buffer):
    parsed_data = []
    
    for item in buffer:
        # Check if the item is the specific string "1512-json-full"
        if item == '"1512-json-full"':
            #print(f"Skipping item: {item}")
            continue
        
        try:
            # Clean the item by replacing escaped quotes and stripping surrounding quotes
            clean_item = item.replace('\\"', '"').strip('"')
            # Attempt to parse the JSON string
            json_data = json.loads(clean_item)
            # Append the parsed JSON object to the list
            parsed_data.append(json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing item: {item}\nError: {e}")
        except Exception as e:
            print(f"Unexpected error with item: {item}\nError: {e}")
    
    return parsed_data

    parsed_data = []
    
    for item in buffer:
        try:
            clean_item=item.replace(''"1512-json-full"',').strip('"')
            print(clean_item)
            # Clean the item by replacing escaped quotes and stripping surrounding quotes
            clean_item = item.replace('\\"', '"').strip('"')
            # Attempt to parse the JSON string
            json_data = json.loads(clean_item)
            # Append the parsed JSON object to the list
            parsed_data.append(json_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing item: {item}\nError: {e}")
        except Exception as e:
            print(f"Unexpected error with item: {item}\nError: {e}")
    
    return parsed_data

def load_holidays(filename):
    holidays = []
    with open(filename, 'r') as f:
        for line in f:
            holidays.append(datetime.strptime(line.strip(), "%Y-%m-%d").date())
    return holidays

def table_exists(table_name, mycursor):
    """Checks if the table exists in the database."""
    mycursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return mycursor.fetchone() is not None

async def create_table_if_not_exists(table_name, pool):
    """Creates the data table if it does not exist."""
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Check if the table already exists
            await cur.execute(f"SHOW TABLES LIKE '{table_name}'")
            if await cur.fetchone() is not None:
                print(f"Table '{table_name}' already exists.")
                return
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

async def start_socketio_client(url, market_token):
    sio.connect(url, 
                headers= {'Content-Type': 'application/json', 'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJQRUdBU1VTQ18xZjQ0MDgzMGFmMWQ4MmE3YTA5MjUxIiwicHVibGljS2V5IjoiMWY0NDA4MzBhZjFkODJhN2EwOTI1MSIsImlhdCI6MTcxODMzNzk1NSwiZXhwIjoxNzE4NDI0MzU1fQ.zx5uDazuT32dUJ2wEH8httKMaK4UJN4ftQWkeHLdcmY'},
                transports='websocket',
                namespaces=None,
                socketio_path='/apimarketdata/socket.io')
    await sio.wait()

def start_socketio_thread(url, market_token):
    asyncio.run(start_socketio_client(url, market_token))

async def main():
    global data_queue
    data_queue = asyncio.Queue()
    # Load NSE holidays
    holidays = load_holidays('nse_holidays.txt')
    today = datetime.today().date()

    # Check if today is Saturday, Sunday, or an NSE holiday
    if today.weekday() >= 5 or today in holidays:
        print("Today is a weekend or an NSE holiday. Exiting.")
        return

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


    fut = fut[(fut['Series']=='OPTIDX') & (fut['Name']=='BANKNIFTY')]

    fut = fut[(fut['ContractExpiration']==fut['ContractExpiration'].min())]

    fut = fut.sort_values(['StrikePrice'])

    fut.reset_index(inplace=True, drop=True)

    fut = fut.sort_values(['StrikePrice'])

    fut = fut[300:400]
    index_futures = fut.copy()
    futures_list = list(set(index_futures['Description']))
    fut_instrument_ids =[]
    for idx in futures_list:
        futures = index_futures[index_futures['Description'] == idx]
        current_expiry = futures.ContractExpiration.min()
        fut_instrument_ids.append(futures['ExchangeInstrumentID'].values[0].item())
    subscribed_symbol = []
    for option in fut_instrument_ids:
        data = {'exchangeInstrumentID': option, 'exchangeSegment': 2}

    current_time = datetime.now()
    combined_token_names = futures_list
    # combined_token_names ={26000 : 'NIFTY 50'}
    # subscribed_symbol =[{'exchangeSegment': 1, 'exchangeInstrumentID': 26000}]
    start_time = current_time.replace(hour=int(start_time.split(':')[0]), minute=int(start_time.split(':')[1]), second=0, microsecond=0)
    end_time = current_time.replace(hour=int(end_time.split(':')[0]), minute=int(end_time.split(':')[1]), second=0, microsecond=0)
    if current_time < start_time:
        time_gap = (start_time - current_time).total_seconds()
        print(f"Sleeping for {time_gap} seconds.")
        #time.sleep(time_gap)

    xts.subscribe_symbols(subscribed_symbol, market_token)
    soc = MDSocket_io(token=market_token, port=port, userID=userid, queue=data_queue)

    soc.on_connect = on_connect
    el = soc.get_emitter()
    el.on('connect', soc.on_connect)
    el.on('1512-json-full', soc.on_message1512_json_full)

    soc.on_message1512_json_full('1512-json-full')
    await soc.connect()
    
    await get_data_queue(data_queue, table_name, end_time, combined_token_names, pool, soc, subscribed_symbol, market_token)
    #asyncio.create_task(monitor_queue(data_queue, table_name, end_time, combined_token_names, pool, soc, subscribed_symbol, market_token))

if __name__ == "__main__":
    asyncio.run(main())
