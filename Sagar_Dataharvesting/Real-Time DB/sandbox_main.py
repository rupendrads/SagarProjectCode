from aifc import Error
import asyncio
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


buffer = []
BULK_INSERT_SIZE = 1500  # Number of records to insert in bulk
MAX_RETRIES = 3  # Maximum number of retries for database connection

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

async def on_connect():
    """Connect from the socket."""
    print('Market Data Socket connected successfully!')
    logger.log('symbols subscribed')



def instrument_generator():
    df = pd.read_csv("nfo.csv", low_memory=False)
    instrument_lists = []

    nifty = df[(df["Series"] == 'OPTIDX') & (df["UnderlyingIndexName"].astype(str).str.upper().str.startswith("NIFTY 50"))]
    expiry = nifty["ContractExpiration"].min()
    nifty = nifty[nifty["ContractExpiration"]==expiry]
    nifty = nifty.sort_values("StrikePrice")
    nifty = nifty[220:280]
    nifty = nifty[["ExchangeInstrumentID", "Description"]]

    instrument_lists = instrument_lists + list(set(nifty.ExchangeInstrumentID))

    banknifty = df[(df["Series"] == 'OPTIDX') & (df["UnderlyingIndexName"].astype(str).str.upper().str.startswith("NIFTY BANK"))]

    expiry = banknifty["ContractExpiration"].min()
    banknifty = banknifty[banknifty["ContractExpiration"]==expiry]
    banknifty = banknifty.sort_values("StrikePrice")
    banknifty = banknifty[220:440]

    banknifty = banknifty[["ExchangeInstrumentID", "Description"]]

    instrument_lists = instrument_lists  + list(set(banknifty.ExchangeInstrumentID))

    nifty_fut = df[(df["Series"] == 'FUTIDX') & (df["UnderlyingIndexName"].astype(str).str.upper().str.startswith("NIFTY 50"))]
    expiry = nifty_fut["ContractExpiration"].min()
    nifty_fut = nifty_fut[nifty_fut["ContractExpiration"]==expiry]

    instrument_lists.append(int(nifty_fut.ExchangeInstrumentID.values[0]))

    banknifty_fut = df[(df["Series"] == 'FUTIDX') & (df["UnderlyingIndexName"].astype(str).str.upper().str.startswith("NIFTY BANK"))]
    expiry = banknifty_fut["ContractExpiration"].min()
    banknifty_fut = banknifty_fut[banknifty_fut["ContractExpiration"]==expiry]

    instrument_lists.append(int(banknifty_fut.ExchangeInstrumentID.values[0]))

    subscribed_symbols =[]
    for instrument in instrument_lists:
        subscribed_symbols.append({"exchangeInstrumentID": instrument, "exchangeSegment":2})
    instrument_lists.append(26000)
    instrument_lists.append(26001)
    subscribed_symbols.append({"exchangeInstrumentID": 26000, "exchangeSegment":1})
    subscribed_symbols.append({"exchangeInstrumentID": 26001, "exchangeSegment":1})
    instrument_names = df[df['ExchangeInstrumentID'].isin(instrument_lists)]

    combined_token_names = instrument_names.set_index('ExchangeInstrumentID')['Description'].to_dict()

    combined_token_names[26000]='NIFTY 50'
    combined_token_names[26001] = 'NIFTY BANK'
    return combined_token_names, subscribed_symbols

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
                        item.get("LastTradedQuantity", None),
                        datetime.fromtimestamp(item.get("LastUpdateTime", None)) - timedelta(minutes=330) if item.get("LastUpdateTime", None) is not None else None,
                        item.get("Close", None),
                        combined_token_names.get(item.get("ExchangeInstrumentID", None), None),
                        json.dumps(item)
                    )
                    for item in buffer
                ]
                await cur.executemany(query, values)
                await conn.commit()
            except Exception as e:
                logger.log(f"Error during bulk insert: {e}")
                await conn.rollback()

async def get_data_queue(queue, table_name, end_time, combined_token_names, pool, soc, subscribed_symbol, market_token):
    buffer = []
    global BULK_INSERT_SIZE 
    while True:
        try:
            if datetime.now() >= end_time:
                logger.log('Time is over, exiting')
                soc.disconnect()
                break

            result = await asyncio.get_event_loop().run_in_executor(None, queue.get)
            if result is None:
                break  # Exit signal

            try:
                data_dict = json.loads(result)
            except json.JSONDecodeError as e:
                print(f'JSON decoding error: {e}')
                continue
            buffer.append(data_dict)

            if len(buffer) >= BULK_INSERT_SIZE:
                try:
                    await bulk_insert_to_db(buffer, table_name, combined_token_names, pool)
                    buffer = []  # Clear the buffer after successful insert
                except Exception as e:
                    print(f"Error during bulk insert: {e}")
        except Empty:
            continue

        except Exception as e:
            logger.log(f'Error in get_data_queue: {e}')
            print(f'Error in get_data_queue: {e}')
            continue

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
                    OverallData TEXT(255)
                )
                """
                await cur.execute(create_table_query)
                print(f"Table '{table_name}' created successfully or already exists.")


async def main():
    
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
    
    await create_table_if_not_exists(table_name,pool)    
    
    print(creds)
    market_token, userid   = broker_login(xts, creds) 
    xts.market_token, xts.userid  = market_token, userid      
    if not isLatestInstrumentFiles():
        xts.update_master_db()
    else:
        print("Already updated nfo and nsecm files")
    data_queue = Queue()
    
    combined_token_names, subscribed_symbol = instrument_generator()
    current_time = datetime.now()
    # index_list = xts.get_index_list(1)['indexList']
    # index_dict = [{'exchangeInstrumentID': int(item.split('_')[1]), 'exchangeSegment': 1} for item in index_list]
    # subscribed_symbol = subscribed_symbol + index_dict
    start_time = current_time.replace(hour=int(start_time.split(':')[0]), minute=int(start_time.split(':')[1]), second=0, microsecond=0)
    end_time = current_time.replace(hour=int(end_time.split(':')[0]), minute=int(end_time.split(':')[1]), second=0, microsecond=0)
    if current_time < start_time:
        time_gap = (start_time - current_time).total_seconds()
        print(f"Sleeping for {time_gap} seconds.")
        time.sleep(time_gap)
    xts.subscribe_symbols(subscribed_symbol, market_token)
    soc = MDSocket_io(token=market_token, port=port, userID=userid, queue=data_queue)
    
    soc.on_connect = on_connect
    el = soc.get_emitter()
    el.on('connect', soc.on_connect)
    el.on('1512-json-full', soc.on_message1512_json_full)
        
    soc.on_message1512_json_full('1512-json-full')
    soc.connect()
    await get_data_queue(data_queue, table_name, end_time, combined_token_names, pool, soc, subscribed_symbol, market_token)

if __name__ == "__main__":
    asyncio.run(main())
