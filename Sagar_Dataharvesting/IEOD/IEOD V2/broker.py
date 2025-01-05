import os
from datetime import datetime
import json
# import socketio
from io import StringIO
import requests
import pandas as pd
# from async_socket import MDSocket_io
class XTSlogin:
    def __init__(self):
        self.market_url = "https://ttblaze.iifl.com/apimarketdata/auth/login" 
        self.master_instruments_url = "https://ttblaze.iifl.com/apimarketdata/instruments/master"
        self.interactive_url = "https://ttblaze.iifl.com/interactive/user/session" 
        self.index_list_url = "https://ttblaze.iifl.com/marketdata/instruments/indexlist"
        self.quote_url = "https://ttblaze.iifl.com/marketdata/instruments/quotes"
        self.cover_order_url = "https://ttblaze.iifl.com/interactive/orders/cover"
        self.limit_order_url = "https://ttblaze.iifl.com/interactive/orders"
        self.historical_url =  "https://ttblaze.iifl.com/apimarketdata/instruments/ohlc"
        self.headers = {
            "Content-Type": "application/json"
        }
    def market_login(self, secret_key, app_key):
        payload = {
            "secretKey": secret_key,
            "appKey": app_key,
            "source": "WebAPI"
        }
        print(payload)

        try:
            response = requests.post(self.market_url, json=payload, headers=self.headers,verify=False)
            data = response.json()
            if data['type'] == 'success':
                token = data['result']['token']
                userid = data['result']['userID']
                self.market_token = token
                return token, userid
        except Exception as e:
            print("Error:", e)
            return None
    def interactive_login(self, secret_key, app_key):
        payload = {
            "secretKey": secret_key,
            "appKey": app_key,
            "source": "WebAPI"
        }

        try:
            response = requests.post(self.interactive_url, json=payload, headers=self.headers)
            data = response.json()
            if data['type'] == 'success':
                token = data['result']['token']
                userid = data['result']['userID']
                self.interactive_token = token
                return token, userid
        except Exception as e:
            print("Error:", e)
            return None
    def get_master(self, exchangeSegmentList):
        try:
            # payload = exchangeSegmentList

            response = requests.post(self.master_instruments_url, json = exchangeSegmentList)

            instrument_details = response.json()['result']
            # print(instrument_details)
            if exchangeSegmentList['exchangeSegmentList']==['NSECM']:
                iifl_instruments = pd.read_csv(StringIO(instrument_details), sep = '|', usecols=range(19), header = None, low_memory=False)
                # new_column_names = ["ExchangeSegment","ExchangeInstrumentID","InstrumentType","Name","Description","Series","NameWithSeries","InstrumentID","PriceBand.High","PriceBand.Low","FreezeQty","TickSize","LotSize","Multiplier","UnderlyingInstrumentId","UnderlyingIndexName","ContractExpiration","StrikePrice","OptionType","DisplayName","PriceNumerator"]
                new_column_names = [
                    "ExchangeSegment",
                    "ExchangeInstrumentID",
                    "InstrumentType",
                    "Name",
                    "Description",
                    "Series",
                    "NameWithSeries",
                    "InstrumentID",
                    "PriceBand.High",
                    "PriceBand.Low",
                    "FreezeQty",
                    "TickSize",
                    "LotSize",
                    "Multiplier",
                    "DisplayName",
                    "ISIN",
                    "PriceNumerator",
                    "PriceDenominator",
                    "DetailedDescription"
                ]

                iifl_instruments.columns = new_column_names
                iifl_instruments.to_csv('nsecm.csv')
            elif exchangeSegmentList['exchangeSegmentList']==['NSEFO']:
                iifl_instruments = pd.read_csv(StringIO(instrument_details), sep = '|', usecols=range(21), header = None, low_memory=False)
                new_column_names = ["ExchangeSegment","ExchangeInstrumentID","InstrumentType","Name","Description","Series","NameWithSeries","InstrumentID","PriceBand.High","PriceBand.Low","FreezeQty","TickSize","LotSize","Multiplier","UnderlyingInstrumentId","UnderlyingIndexName","ContractExpiration","StrikePrice","OptionType","DisplayName","PriceNumerator"]
                iifl_instruments.columns = new_column_names
                iifl_instruments['ContractExpiration'] = pd.to_datetime(iifl_instruments['ContractExpiration']).dt.date
                iifl_instruments.to_csv('nfo.csv')
            return iifl_instruments
        except Exception as e:
            print(e)

    def update_master_db(self):
        iifl_master = self.get_master({'exchangeSegmentList': ['NSEFO']})
        iifl_master = self.get_master({'exchangeSegmentList': ['NSECM']})
        # iifl = iifl_master[['ExchangeInstrumentID', 'Description', 'ContractExpiration','UnderlyingIndexName', 'StrikePrice', 'OptionType', 'ExchangeSegment', 'FreezeQty', 'LotSize', 'Series']]
        # iifl.to_csv('nfo.csv')
        print('master csv updated')
    def get_index_list(self, exchangeSegment):
        try:
            response = requests.get(self.index_list_url, params = {"exchangeSegment": exchangeSegment})
            data = response.json()
            if data['type']=="success":
                return data["result"]
            else:
                return None
        except Exception as e:
            print("Error:", e)
            return None
        
    def get_quotes(self, instruments):
            headers = self.headers
            headers.update({'Authorization': self.market_token})
            payload = {"instruments": instruments, "xtsMessageCode": 1512, "publishFormat" : "JSON" }
            try:
                response = requests.post(self.quote_url,json= payload, headers=headers)
                # print(response.json())
                return response.json()
            except Exception as e:
                print(e)
                return None
    def place_cover_order(self, params):
        headers = self.headers
        headers.update({'Authorization': self.interactive_token})
        # payload = params
        try:
            params["exchangeSegment"]="NSEFO"
            # params["productType"] ="MIS"
            params["orderType"]="LIMIT"
            # params["timeInForce"]="DAY"
            params["disclosedQuantity"]=0
            # params["limitPrice"]=0
            params["orderUniqueIdentifier"]= f'{params["exchangeInstrumentID"]}'
            
            payload = params
            response = requests.post(self.cover_order_url, json = payload,headers=headers)
            return response.json()
        except Exception as e:
            print(e)
            return None
        
    def place_limit_order(self, params):
        headers = self.headers
        headers.update({'Authorization': self.interactive_token})
        try:
            params["exchangeSegment"]="NSEFO"
            params["productType"] ="NRML"
            params["orderType"]="LIMIT"
            params["timeInForce"]="DAY"
            params["disclosedQuantity"]=0
            params["orderUniqueIdentifier"]= f'{params["exchangeInstrumentID"]}'
            payload = params
            response = requests.post(self.limit_order_url, json = payload,headers=headers)
            return response.json()
        except Exception as e:
            print(e)
            return None
        
    def subscribe_symbols(self, instruments,market_token):
        subscription_url = "https://ttblaze.iifl.com/apimarketdata/instruments/subscription"

        params = {'instruments': instruments, 'xtsMessageCode': 1512}
        session = requests.Session()
        headers = self.headers
        headers.update({'Authorization': self.market_token})
        
        try:
            r = session.request("POST",
                                        subscription_url,
                                        data=json.dumps(params),
                                        params=None,
                                        headers=headers
                                        )
            # print(r.content)
        except Exception as e:
            raise e
        
    def get_historical_data(self, params):
        headers = self.headers
        headers.update({'Authorization': self.market_token})
        try:
            params = params
            response = requests.get(self.historical_url, params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print("Failed to retrieve data. Status code:", response.status_code)
                print("Response:", response.text)
                return None
        except Exception as e:
            print("Exception occurred:", e)
            return None
    def update_master_db(self):
        iifl_master = self.get_master({'exchangeSegmentList': ['NSEFO']})
        # iifl = iifl_master[['ExchangeInstrumentID', 'Description', 'ContractExpiration','UnderlyingIndexName', 'StrikePrice', 'OptionType', 'ExchangeSegment', 'FreezeQty', 'LotSize', 'Series']]
        # iifl.to_csv('nfo.csv')
        iifl_master = self.get_master({'exchangeSegmentList': ['NSECM']})