import asyncio
from datetime import datetime
from MarketSocketStream import MDSocket_io
from InteractiveSocket import OrderSocket_io
from datetime import datetime
from Broker import XTS
from creds import creds, range_percentage
from utils import  broker_login
from Publisher import Publisher
import time
import pandas as pd
publisher = Publisher()
# create_tradebook_table()
import warnings
import asyncio
import json
warnings.filterwarnings("ignore")
port = "https://ttblaze.iifl.com"
def get_exchange_instrument_id(instrument_name):
    for instrument in index_instruments:
        if instrument['name'].upper() == instrument_name.upper():
            return instrument['exchangeInstrumentID']
        
def filter_options(index_name, index_ranges, index_options):
    """
    Filters options for a given index name based on its range and contract expiration.
    
    Parameters:
    - index_name (str): The name of the index (e.g., 'NIFTY 50').
    - index_ranges (dict): A dictionary containing low and high ranges for each index.
    - index_options (pd.DataFrame): DataFrame containing options data.

    Returns:
    - List of dictionaries with exchangeInstrumentID and exchangeSegment.
    """
    # Get the exchangeInstrumentID for the given index
    exchange_id = get_exchange_instrument_id(index_name)
    if not exchange_id:
        return []  
    
    # Get the range for the index
    index_range = index_ranges.get(str(exchange_id))
    if not index_range:
        return []  
    low = index_range['low']
    high = index_range['high']
    
    options = index_options[index_options['UnderlyingIndexName'].str.upper() == index_name.upper()]
    options = options[options['ContractExpiration'] == min(options['ContractExpiration'])]
    options = options[(options['StrikePrice'] >= float(low)) & (options['StrikePrice'] <= float(high))]
    
    return options[['ExchangeInstrumentID', 'Description']].apply(
        lambda row: {'exchangeInstrumentID': row['ExchangeInstrumentID'], 'exchangeSegment': 2},
        axis=1
    ).tolist()
xts = XTS()  

market_token, interactive_token, userid = broker_login(xts, creds)
xts.market_token, xts.interactive_token, xts.userid  = market_token, interactive_token, userid
xts.update_master_db()
soc = MDSocket_io(token = market_token, port=port, userID=userid,publisher=publisher)
soc.connect()
# xts.subscribe_symbols([{'exchangeInstrumentID': 26000, 'exchangeSegment':1}])
index_instruments = [
    {'name': 'NIFTY 50', 'exchangeInstrumentID': 26000, 'exchangeSegment': 1},
    {'name': 'NIFTY BANK', 'exchangeInstrumentID': 26001, 'exchangeSegment': 1},
    {'name': 'NIFTY FIN SERVICE', 'exchangeInstrumentID': 26034, 'exchangeSegment': 1},
    {'name': 'NIFTY MID SELECT', 'exchangeInstrumentID': 26121, 'exchangeSegment': 1}
    # {'name': 'SENSEX', 'exchangeInstrumentID': 26065, 'exchangeSegment': 11},
    # {'name': 'BANKEX', 'exchangeInstrumentID': 26118, 'exchangeSegment': 11}
]

instruments_list = [{'exchangeInstrumentID': instrument['exchangeInstrumentID'], 
                   'exchangeSegment': instrument['exchangeSegment']} for instrument in index_instruments]

# # Nifty 26000, BankNifty 26001, FinNifty 26034, MidcpNifty 26121, Sensex 26065, and Bankex 26118

instruments = pd.read_csv('nfo.csv', low_memory=False)
index_futures = instruments[instruments['Series']=='FUTIDX']
nifty_fut = index_futures[index_futures['UnderlyingIndexName'].str.upper()=='NIFTY 50']
nifty_fut = nifty_fut.sort_values('ContractExpiration').head(2)
banknifty_fut = index_futures[index_futures['UnderlyingIndexName'].str.upper()=='NIFTY BANK']
banknifty_fut = banknifty_fut.sort_values('ContractExpiration').head(2)
finnifty_fut = index_futures[index_futures['UnderlyingIndexName'].str.upper()=='NIFTY FIN SERVICE']
finnifty_fut = finnifty_fut.sort_values('ContractExpiration').head(2)
midcpnifty_fut = index_futures[index_futures['UnderlyingIndexName'].str.upper()=='NIFTY MID SELECT']
midcpnifty_fut = midcpnifty_fut.sort_values('ContractExpiration').head(2)
all_futures = pd.concat([nifty_fut, banknifty_fut, finnifty_fut, midcpnifty_fut]).reset_index(drop=True)
all_futures = all_futures[['ExchangeInstrumentID', 'Description']]
index_fut_list = all_futures.apply(
    lambda row: {'exchangeInstrumentID': row['ExchangeInstrumentID'], 'exchangeSegment': 2},
    axis=1
).tolist()
# print(index_fut_list)
with open('index_range.json', 'r') as f:
        index_ranges = json.load(f)
index_options = instruments[instruments['Series']=='OPTIDX']
index_options['StrikePrice']= index_options['StrikePrice'].astype(int)

index_names = ['NIFTY 50', 'NIFTY BANK', 'NIFTY FIN SERVICE', 'NIFTY MID SELECT']
combined_list = []

for index_name in index_names:
    combined_list.extend(filter_options(index_name, index_ranges, index_options))
combined_list.extend(index_fut_list)
# print(len(combined_list))
xts.subscribe_symbols(combined_list)
# index_options['StrikePrice']= index_options['StrikePrice'].astype(int)
# nifty_options = index_options[index_options['UnderlyingIndexName'].str.upper()=='NIFTY 50']
# nifty_options = nifty_options[nifty_options['ContractExpiration']==min(nifty_options['ContractExpiration'])]

# nifty_exchange_id = get_exchange_instrument_id('NIFTY 50')
# nifty_range = index_ranges.get(str(nifty_exchange_id))
# if nifty_range:
#     low = nifty_range['low']
#     high = nifty_range['high']
#     print(low, high)
#     nifty_options = nifty_options[
#         (nifty_options['StrikePrice'] >= float(low)) & (nifty_options['StrikePrice'] <= float(high))
#     ]
# nifty_options = nifty_options[['ExchangeInstrumentID', 'Description']]
# nifty_options_list = nifty_options.apply(
#     lambda row: {'exchangeInstrumentID': row['ExchangeInstrumentID'], 'exchangeSegment': 2},
#     axis=1
# ).tolist()

# print(nifty_options_list)
# print(index_fut_list + nifty_options_list)
# xts.subscribe_symbols(index_fut_list)
# index_options = instruments[instruments['Series']=='OPTIDX']
# nifty_options = index_options[index_options['UnderlyingIndexName'].str.upper()=='NIFTY 50']
# nifty_expiry = list(set(index_options.ContractExpiration))
# nifty_expiry.sort()
# nifty_expiry= nifty_expiry[0]
# quotes = xts.get_quotes(instruments_list)
# ltp_list = [{'ExchangeInstrumentID': json.loads(quote)['ExchangeInstrumentID'], 'ltp': json.loads(quote)['LastTradedPrice']} 
#             for quote in quotes['result']['listQuotes']]
# print(ltp_list)
# index_ranges = {}

# # xts.update_master_db()
# for quote in quotes['result']['listQuotes']:
#     quote_data = json.loads(quote)
#     exchange_id = quote_data['ExchangeInstrumentID']
#     last_price = quote_data['LastTradedPrice']
#     range_value = (last_price * range_percentage) / 100
#     index_ranges[exchange_id] = {
#         'low': round(last_price - range_value,2),
#         'high': round(last_price + range_value,2)
#     }

# # Save to JSON file
# with open('index_range.json', 'w') as file:
#     json.dump(index_ranges, file, indent=4)


# fut = pd.read_csv('nfo.csv', low_memory=False)
# index_options = fut[(fut.Series == 'OPTIDX') & (fut["Name"].isin(["NIFTY"])) & (fut["UnderlyingIndexName"].isin(["Nifty 50"]))]
# index_options = index_options[index_options.ContractExpiration == min(index_options.ContractExpiration)]
# index_options = index_options.set_index('ExchangeInstrumentID')['Description'].to_dict()
# subscribed_symbols = []
# for instrument_id, name in index_options.items():
#     subscribed_symbols.append([{'exchangeInstrumentID': instrument_id, 'exchangeSegment': 2}])

# xts.subscribe_symbols(index_fut_list)


# while True:
#     time.sleep(10)
#     soc.verify_message_counts()



# finnifty: strike_range 50
# midcapnifty: strike range 25

# nifty strike range 50
# banknifty 100
# sensex, bank 100