from utils import filter_dataframe
import re
import json
import pandas as pd
from utils import get_atm
import time
from io import StringIO
from datetime import datetime, timedelta
import asyncio
from utils import Logger, update_tradebook, slice_orders
class LegBuilder:
    def __init__(self, xts, soc, interactive_soc, leg_name, strategy, publisher, total_lots, position, option_type, expiry, strike_selection_criteria, strike, roll_strike,
                 new_strike_selection_criteria, stop_loss, trailing_sl, no_of_reentry, simple_momentum=False, range_breakout=False):
        self.xts = xts
        self.pegasus = Logger('pegasus.txt')
        self.soc = soc
        self.leg_name = leg_name
        self.interactive = interactive_soc
        self.strategy = strategy
        self.publisher = publisher
        self.total_lots = total_lots
        self.position = position
        self.option_type = 3 if option_type == 'CE' else 4
        self.expiry = 0 if expiry == 'current' else (1 if expiry=='next_expiry' else 2 if expiry == 'monthly' else None)
        self.strike_selection_criteria = strike_selection_criteria
        self.strike = strike
        self.roll_strike = roll_strike
        # self.new_strike_selection_criteria = new_strike_selection_criteria
        self.stop_loss = stop_loss
        self.trailing_sl = trailing_sl
        self.no_of_reentry = no_of_reentry
        self.reentry_count = 0
        self.simple_momentum = simple_momentum
        self.range_breakout = range_breakout
        self.current_price = None
        self.current_profit_loss = 0  
        self.order_status = None
        self.assign_strategy_variables()
        self.expiry_df = self.get_expiry_df()
        self.trade_data = []
        self.tradebook = []
        self.market_data =[]
        self.trigger_tolerance = 2
        self.trade_position = None
        self.max_profit = 0
        self.max_loss = 0
        self.pnl = 0 
        self.sl_price = 0
        self.trade_data_event = asyncio.Event()
        self.market_data_event = asyncio.Event()
        self.realised_pnl = 0
    def assign_strategy_variables(self):
        # self.strike = self.strategy.strike
        self.index = self.strategy.index
        self.df = self.strategy.df        
        # print(self.freeze_quantity)
        self.base = 100 if self.strategy.index == 'NIFTY BANK' else 50
    def update_price(self, price):
        self.current_price = price


    async def receive_trades(self,data):
        print(f'trade data received from publisher for {self.leg_name}')#and data is \n {data}')
        self.trade_data.append(data)
        print('trade data has been appended')
        try:
            dt = datetime.strptime(data['ExchangeTransactTimeAPI'], '%d-%m-%Y %H:%M:%S')
            data['ExchangeTransactTimeAPI'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            dt = datetime.strptime(data['ExchangeTransactTimeAPI'], '%Y-%m-%d %H:%M:%S')
            data['ExchangeTransactTimeAPI'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        # print(data)
        if not  data['OrderUniqueIdentifier'].endswith('sl'):
            self.trade_data_event.set()
        
        # update_tradebook(data, self.sl_price)
        # print(self.market_data[-1:])
        if data['OrderUniqueIdentifier'].endswith('sl'):
            update_tradebook(data, self.sl_price)
            self.trade_position = None
            print('changed trade_position to none')
            print(f'no of renentry {self.no_of_reentry} and reentry count {self.reentry_count}')
            if (self.no_of_reentry) and (self.no_of_reentry> self.reentry_count):
                    print('checking for reentry')
                    self.reentry_count = self.reentry_count + 1
                    print('running re entry logic')
                    await self.reentry_logic()
                    
            else:
             pass
        elif data['OrderUniqueIdentifier'].endswith('momentum'):
            self.trade_position = True
            self.xts.place
            update_tradebook(data, self.entry_price)
        elif data['OrderUniqueIdentifier'].endswith('cover'):
            update_tradebook(data)
            print("updated db for covering pending orders")

        else:
            update_tradebook(data, self.entry_price)

        self.pegasus.log(data)
        print(data['ExchangeTransactTimeAPI'])
        print(f'trade data appended')


    async def receive_data(self,data):
        # print(f'socket data from publisher for {self.leg_name} and data is \n {data["ExchangeInstrumentID"]}, {data["LastTradedPrice"]}')
        self.market_data.append(data)
        self.market_data_event.set()
        # print(self.market_data)

    async def reentry_logic(self):
        print('inside reentry function')
        order_placed=False
        
        while True :
            time_now = datetime.now()
            if self.strategy.last_entry_time > time_now:
                current_price = self.market_data[-1:][0]
                current_price = current_price['LastTradedPrice']
                if (self.position.lower() =='buy') and (not order_placed):
                    if current_price >= self.entry_price:
                        print(f'current price {current_price} has come back to entry_price {self.entry_price}')
                        print('re-entering the trade')
                        
                        order = self.xts.place_market_order({"exchangeInstrumentID": self.instrument_id, "orderSide": self.position,
                                                            "orderQuantity":int(self.lot_size) *self.total_lots,"limitPrice":0,
                                                                "stopPrice": 1, "orderUniqueIdentifier": self.leg_name})

                        order_placed=True
                        print('breaking out of while loop')
                        break
                elif (self.position.lower()=='sell') and (not order_placed):
                    if current_price <= self.entry_price:
                        print(f'current price {current_price} has come back to entry_price {self.entry_price}')
                        print('re-entering the trade')
                        
                        order = self.xts.place_market_order({"exchangeInstrumentID": self.instrument_id, "orderSide": self.position,
                                                            "orderQuantity":int(self.lot_size) *self.total_lots,"limitPrice":0,
                                                                "stopPrice": 1, "orderUniqueIdentifier": self.leg_name})

                        order_placed=True
                        print('breaking out of while loop')
                        break
            else:
                # print('last entry time is over')
                pass
        if order_placed:
            print('waiting for trade data')
            # await self.trade_data_event.wait()
            #optimize it
            await asyncio.sleep(5)
            print('wait is over in reentry logic')
            latest_trade = self.trade_data[-1:][0]
            if latest_trade['OrderStatus']=='Filled':
                order_placed=False
                self.trade_entry_price = float(latest_trade['OrderAverageTradedPrice'])
                trade_side = latest_trade['OrderSide']
                traded_quantity = latest_trade['OrderQuantity']
                entry_timestmap = latest_trade['ExchangeTransactTime']
                entry_slippage = self.trade_entry_price - self.entry_price
                trade = {'symbol': self.instrument_id, 'entry_price': self.entry_price, 'trade_price': self.trade_entry_price,  'trade' : trade_side, 'quantity' : traded_quantity, 'timestamp': entry_timestmap, 'entry_slippage': round((self.entry_price - self.trade_entry_price), 2)}
                # print(f'instrument traded at avg price of {self.trade_entry_price}, side {trade_side},\n with quantity {traded_quantity} and executed at  {entry_timestmap} and slippage is {entry_slippage}')
                # print(trade)
            # print(f'placing SL order now for {self.leg_name} SL points {self.stop_loss}')
            # if self.stop_loss[0].lower()=='points':
            #     self.stop_loss = self.stop_loss[1]
            # elif self.stop_loss[0].lower() == 'percent':
            #     self.stop_loss = round(self.trade_entry_price*self.stoploss[1]/100, 2)
            if trade_side.upper() == 'BUY':
                self.trade_position = 'long'
                print('trade position is long')
                self.sl_price = self.trade_entry_price - self.stop_loss
                trigger_price = self.sl_price - self.trigger_tolerance
            else: 
                self.trade_position = 'short'
                print('trade position is short')
                self.sl_price = self.trade_entry_price + self.stop_loss
                trigger_price = self.sl_price + self.trigger_tolerance
            orderSide = trade_side #'BUY' if trade_side.upper() == 'SELL' else 'SELL'
            orderid = f"{self.leg_name}_sl"
            print({"exchangeInstrumentID": self.instrument_id, "orderSide": orderSide,
                                            "orderQuantity":traded_quantity,
                                              "limitPrice": trigger_price, 'stopPrice':self.sl_price, 'orderUniqueIdentifier': orderid})
            order =  self.xts.place_SL_order({"exchangeInstrumentID": self.instrument_id, "orderSide": orderSide,
                                            "orderQuantity":traded_quantity, "limitPrice": trigger_price, 'stopPrice':self.sl_price, 'orderUniqueIdentifier': orderid})    
            self.trade_data_event.clear()
    
    async def stoploss_trail(self, ltp, trade_position):

        # print("inside stoploss_trail function")
        if (self.trailing_sl) and trade_position =='long':
            price_gap = ltp - self.entry_price
            if price_gap > self.trailing_sl["priceMove"]:
                orders = self.interactive.orders

                trail_increment_factor = price_gap//self.trailing_sl["priceMove"]
                original_sl = self.trade_entry_price - self.stop_loss
                updated_sl = original_sl + trail_increment_factor*self.trailing_sl["sl_adjustment"]
                if updated_sl > self.sl_price:
                    print(f"sl {self.sl_price} adjusted to {updated_sl} current_price is {ltp} and entry_price {self.entry_price} in {self.leg_name}")
                    self.sl_price = updated_sl
                    order_uid = f"{self.leg_name}_sl"
                    for order in orders[::-1]:
                        print(order)
                        if order["orderUniqueIdentifier"] ==order_uid:
                            app_id = order["appOrderID"]
                            print(f"type of app_id is {type(app_id)} {app_id}")
                            break
                    params = {
                        "appOrderID": app_id,
                        "modifiedProductType": "NRML",
                        "modifiedOrderType": "STOPLIMIT",
                        "modifiedOrderQuantity": self.lot_size*self.total_lots,
                        "modifiedDisclosedQuantity": 0,
                        "modifiedLimitPrice": float(updated_sl-self.trigger_tolerance),
                        "modifiedStopPrice": float(updated_sl),
                        "modifiedTimeInForce": "DAY",
                        "orderUniqueIdentifier": order_uid
                        }
                    self.xts.modify_order(params)
                else:
                    pass
        elif (self.trailing_sl) and (trade_position=='short') :       
            price_gap = self.entry_price - ltp 
            if price_gap > self.trailing_sl["priceMove"]:
                orders = self.interactive.orders
                print(self.stop_loss, self.trade_entry_price)
                trail_increment_factor = price_gap//self.trailing_sl["priceMove"]
                original_sl =  self.stop_loss + self.trade_entry_price
                updated_sl = original_sl - trail_increment_factor*self.trailing_sl["sl_adjustment"]
                if updated_sl < self.sl_price:
                    print(f"sl {self.sl_price} adjusted to {updated_sl} current_price is {ltp} and entry_price {self.entry_price}")
                    self.sl_price = updated_sl
                    order_uid = f"{self.leg_name}_sl"
                    for order in orders[::-1]:
                        if order["OrderUniqueIdentifier"] ==order_uid:
                            
                            app_id = order["AppOrderID"]
                           
                            break
                    params = {
                        "appOrderID": app_id,
                        "modifiedProductType": "NRML",
                        "modifiedOrderType": "STOPLIMIT",
                        "modifiedOrderQuantity": int(self.lot_size*self.total_lots),
                        "modifiedDisclosedQuantity": 0,
                        "modifiedLimitPrice": float(updated_sl+self.trigger_tolerance),
                        "modifiedStopPrice": float(updated_sl),
                        "modifiedTimeInForce": "DAY",
                        "orderUniqueIdentifier": order_uid
                        }
                    self.xts.modify_order(params)

                else:
                    pass
            

             

    def get_expiry_df(self):
        """
        Retrieve a df containing options data for a specific expiry date.

        Parameters:
        - self.df: df containing the complete options data.
        - self.index: Index used for filtering the DataFrame.
        - self.expiry: Integer representing the index of the expiry date to retrieve.
        - self.option_type: String indicating the type of option (e.g., 'call' or 'put') to filter.
        
        Returns:
        - expiry_df: df containing options data filtered for the specified expiry date and option type.
        """
        self.opt_df, self.monthly_expiry_list = filter_dataframe(self.df, [self.index])
        expiry_list = list(set(self.opt_df['expiry']))
        expiry_list.sort()
        if (self.expiry == 2) & (expiry_list[0]== self.monthly_expiry_list[0]):
            expiry_day = self.monthly_expiry_list[1]
        elif((self.expiry == 2)):
            expiry_day = self.monthly_expiry_list[0]
        else:
            expiry_day = expiry_list[self.expiry]
        self.combined_expiry_df = self.opt_df[(self.opt_df['expiry']== expiry_day)]
        expiry_df = self.opt_df[(self.opt_df['expiry']== expiry_day) & (self.opt_df['option_type']==self.option_type)] #& (self.option_type['strike']==self.strike)]
        return expiry_df
    
    def selection_criteria(self):
        """
            Apply selection criteria based on user-defined parameters to determine the option to be traded.
        """
        choice = self.strike_selection_criteria['strike_selection']
        choice_value = self.strike_selection_criteria['value']
        print(f'leg opted for {choice} and select strike is {choice_value}')
        if  choice == 'strike':
            if choice_value=='ATM':
                
                self.option_symbol = self.expiry_df[(self.expiry_df['strike'].astype(int)== self.strike)]
                self.instrument_id = int(self.option_symbol['instrument_token'].values[0])
                print(self.option_symbol)
                self.lot_size = int(self.option_symbol['lot_size'].values[0])
            elif choice_value.startswith('ITM'):
                itm_depth = re.findall(r'\d+', choice_value)
                if itm_depth:
                    if self.option_type == 3:
                        self.strike = self.strike - 100*int(itm_depth[0])
                        self.option_symbol = self.expiry_df[(self.expiry_df['strike'].astype(int)== self.strike)]
                        print(self.option_symbol)
                        self.instrument_id = int(self.option_symbol['instrument_token'].values[0])
                        self.lot_size = int(self.option_symbol['lot_size'].values[0])
                    else:
                        self.strike = self.strike + 100*int(itm_depth[0])
                        self.option_symbol = self.expiry_df[(self.expiry_df['strike'].astype(int)== self.strike)]
                        self.instrument_id = int(self.option_symbol['instrument_token'].values[0])
                        print(self.option_symbol)
                        self.lot_size = int(self.option_symbol['lot_size'].values[0])
            elif choice_value.startswith('OTM'):
                itm_depth = re.findall(r'\d+', choice_value)
                if itm_depth:
                    if self.option_type == 3:
                        self.strike = self.strike + 100*int(itm_depth[0])
                        self.option_symbol = self.expiry_df[(self.expiry_df['strike'].astype(int)== self.strike)]
                        print(self.option_symbol)
                        self.instrument_id = int(self.option_symbol['instrument_token'].values[0])
                        self.lot_size = int(self.option_symbol['lot_size'].values[0])
                        
                    else:
                        self.strike = self.strike - 100*int(itm_depth[0])
                        self.option_symbol = self.expiry_df[(self.expiry_df['strike'].astype(int)== self.strike)]
                        self.instrument_id = int(self.option_symbol['instrument_token'].values[0])
                        print(self.option_symbol)
                        self.lot_size = int(self.option_symbol['lot_size'].values[0])
        elif choice.lower() =='closest_premium':
            premium = choice_value
            premium_instruments = []
            exid_list = list(self.expiry_df['instrument_token'])
            ltp_list = []
            chunks = [exid_list[i:i+50] for i in range(0, len(exid_list), 50)]
            exchange_instrument_ids = []
            last_traded_prices = []
            option_types =[]
            for chunk in chunks:
                premium_instruments_chunk = []
                for exid in chunk:
                    premium_instruments_chunk.append({'exchangeSegment': 2, 'exchangeInstrumentID': exid})
                
                response = self.xts.get_quotes(premium_instruments_chunk)
                ltp_data = response['result']['listQuotes']
                for item in ltp_data:
                    item_dict = eval(item)
                    exchange_instrument_ids.append(item_dict['ExchangeInstrumentID']) 
                    last_traded_prices.append(item_dict['LastTradedPrice'])

            df = pd.DataFrame({
                'exchangeInstrumentID': exchange_instrument_ids,
                'LastTradedPrice': last_traded_prices,
            })
            df['PriceDifference'] = abs(df['LastTradedPrice'] - choice_value)
            option_data_sorted = df.sort_values(by='PriceDifference')
            nearest_option = option_data_sorted.iloc[0]
            nearest_premium= nearest_option.LastTradedPrice
            self.instrument_id = int(nearest_option.exchangeInstrumentID)
            nearest_option_name = self.expiry_df[self.expiry_df['instrument_token']== self.instrument_id]
            self.lot_size = nearest_option_name.iloc[0].lot_size
            print(f"{nearest_option_name.iloc[0].tradingsymbol} has premium of {nearest_premium}")

        elif choice.lower() in ['straddle_width', 'atm_pct', 'atm_straddle_premium']:
            straddle_df = self.combined_expiry_df[self.combined_expiry_df['strike'].astype(int)==int(self.strike)]
            options_list = []
            instrument_tokens = list(straddle_df['instrument_token'])
            for instrument_token in instrument_tokens:
                options_list.append({'exchangeSegment':2, 'exchangeInstrumentID': instrument_token})
            results = self.xts.get_quotes(options_list)
            if results['type']=='success':
                ltp_data = results['result']['listQuotes']
            combined_premium = 0
            for ltp_item in ltp_data:
                ltp_value = json.loads(ltp_item)
                ltp = ltp_value['LastTradedPrice']
                combined_premium  = combined_premium + ltp
            
            print(f'combined premium is {combined_premium}') 
            if choice.lower() == 'atm_straddle_premium':
                combined_premium = round(((combined_premium*choice_value)/100), 2)
                print(f'atm_straddle_premium has {combined_premium} value ')
                premium = combined_premium
                premium_instruments = []
                exid_list = list(self.expiry_df['instrument_token'])
                ltp_list = []
                chunks = [exid_list[i:i+50] for i in range(0, len(exid_list), 50)]
                exchange_instrument_ids = []
                last_traded_prices = []
                option_types =[]
                for chunk in chunks:
                    premium_instruments_chunk = []
                    for exid in chunk:
                        premium_instruments_chunk.append({'exchangeSegment': 2, 'exchangeInstrumentID': exid})
                    
                    response = self.xts.get_quotes(premium_instruments_chunk)
                    ltp_data = response['result']['listQuotes']
                    for item in ltp_data:
                        item_dict = eval(item)
                        exchange_instrument_ids.append(item_dict['ExchangeInstrumentID']) 
                        last_traded_prices.append(item_dict['LastTradedPrice'])

                df = pd.DataFrame({
                    'exchangeInstrumentID': exchange_instrument_ids,
                    'LastTradedPrice': last_traded_prices,
                })
                df['PriceDifference'] = abs(df['LastTradedPrice'] - premium)
                option_data_sorted = df.sort_values(by='PriceDifference')
                nearest_option = option_data_sorted.iloc[0]
                nearest_premium= nearest_option.LastTradedPrice
                self.instrument_id = int(nearest_option.exchangeInstrumentID)
                nearest_option_name = self.expiry_df[self.expiry_df['instrument_token']== self.instrument_id]
                self.lot_size = nearest_option_name.iloc[0].lot_size
                print(f"{nearest_option_name.iloc[0].tradingsymbol} has premium of {nearest_premium}")
            

            elif choice.lower() == 'atm_pct':
                if choice_value['atm_strike']== '+':
                    atm_points = choice_value['input']*self.strike
                    self.strike = get_atm(self.strike+atm_points, self.base)
                elif choice_value['atm_strike']== '-':
                    atm_points = choice_value['input']*self.strike
                    self.strike = get_atm(self.strike-atm_points, self.base)
                selected_option = self.expiry_df[self.expiry_df['strike'].astype(int) == self.strike].iloc[0]
                self.instrument_id = int(selected_option.instrument_token)
                self.lot_size = selected_option.lot_size
                print(selected_option.tradingsymbol)

                # combined_premium = round((choice_value* combined_premium)/100)
                
            elif choice_value['atm_strike'] == '+':
                selected_strike = self.strike + combined_premium*choice_value['input']
                print(self.strike)
                selected_strike = get_atm(selected_strike, self.base)
                print(f'selected strike is {selected_strike}')
                self.strike = selected_strike
                selected_option = self.expiry_df[self.expiry_df['strike'].astype(int) == self.strike].iloc[0]
                self.instrument_id = int(selected_option.instrument_token)
                self.lot_size = selected_option.lot_size
                print(selected_option.tradingsymbol)

            elif choice_value['atm_strike'] == '-':
                selected_strike = self.strike - combined_premium*choice_value['input']
                print(self.strike)
                selected_strike = get_atm(selected_strike, self.base)
                print(f'selected strike is {selected_strike}')
                self.strike = selected_strike
                selected_option = self.expiry_df[self.expiry_df['strike'].astype(int) == self.strike].iloc[0]
                self.instrument_id = int(selected_option.instrument_token)
                self.lot_size = selected_option.lot_size
                print(selected_option.tradingsymbol)

        self.xts.subscribe_symbols([{'exchangeSegment': 2, 'exchangeInstrumentID': self.instrument_id}])
        response = self.xts.get_quotes([{'exchangeSegment': 2, 'exchangeInstrumentID': self.instrument_id}])
        ltp_data = response['result']['listQuotes']
        ltp = json.loads(ltp_data[0])['LastTradedPrice']
        self.entry_price = float(ltp)
        # print(f'entry_price before placing order is {self.entry_price}')
        if self.range_breakout:
            timeframe = self.range_breakout['timeframe']
            start_time = self.strategy.entry_time
            end_time = start_time + timedelta(minutes=timeframe)
            start_time = start_time.strftime('%b %d %Y %H%M%S')
            end_time = end_time.strftime('%b %d %Y %H%M%S')
            # trade_side = self.range_breakout['']
            params = {
                "exchangeSegment": 2,
                "exchangeInstrumentID": self.instrument_id,
                "startTime": start_time,
                "endTime": end_time,
                "compressionValue": 60
            }
            print(params)
            print(f'sleeping for {timeframe} minutes')
            time.sleep(timeframe*60)
            data= self.xts.get_historical_data(params)['result']['dataReponse']
            data = data.replace(',', '\n')
            historical_data = pd.read_csv(StringIO(data), sep = '|', usecols=range(7), header = None, low_memory=False)
            new_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi']
            historical_data.columns = new_columns
            # historical_data['instrument_token'] = exchange_instrument_id
            # historical_data['tradingsymbol'] = tradingsymbol
            historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'], unit='s')
            print(historical_data)
            print(f"highest high is {max(historical_data['high'])}, and low is {min(historical_data['low'])}")
            if self.range_breakout['side'].lower()=='high':
                self.entry_price = max(historical_data['high'])
                print(f'high of range is {self.entry_price}')
            elif self.range_breakout['side'].lower()=='low':
                self.entry_price = min(historical_data['low'])
                print('low of range is {self.entry_price}')
            if self.position.lower() == 'buy':
                limit_price = int(self.entry_price)
                trigger_price = int(self.entry_price + self.trigger_tolerance)
            elif self.position.lower() == 'sell':
                limit_price = float(self.entry_price)
                trigger_price = float(self.entry_price - self.trigger_tolerance)
            print(trigger_price, self.entry_price, self.position)
            print(f"Range for {self.range_breakout['timeframe'] is  min(historical_data['low']) and  max(historical_data['high']) }")
            print(f"User selected {self.range_breakout['side']} option, and entry price is {self.entry_price}")
            # self.freeze_quantity = int(self.df[[self.df.instrument_token]==self.instrument_id].FreezeQty.values[0])-1
            order =  self.xts.place_SL_order({"exchangeInstrumentID": self.instrument_id, "orderSide": self.position, "orderQuantity":int(self.total_lots * self.lot_size), "limitPrice": trigger_price, 'stopPrice':self.entry_price, 'orderUniqueIdentifier': 'rb'})
            print('order placed for range breakout')
            print(order)
        elif self.simple_momentum:
            if self.simple_momentum['value_type'].lower()=='points':
                sm_value = self.simple_momentum['value']
            elif self.simple_momentum['value_type'].lower()=='percentage':
                sm_value = round((self.entry_price*self.simple_momentum['value'])/100, 2)
            if self.simple_momentum['direction'].lower() =='increment':
                self.entry_price = self.entry_price + sm_value
            elif self.simple_momentum['direction'].lower() =='decay':
                self.entry_price = self.entry_price - sm_value
            if self.position.lower() == 'buy':
                limit_price = int(self.entry_price)
                trigger_price = int(self.entry_price + self.trigger_tolerance)
            elif self.position.lower() == 'sell':
                limit_price = float(self.entry_price)
                trigger_price = float(self.entry_price - self.trigger_tolerance)
            print(trigger_price, self.entry_price, self.position)
            
            # self.freeze_quantity = int(self.df[[self.df.instrument_token]==self.instrument_id].FreezeQty.values[0])-1
            order =  self.xts.place_SL_order({"exchangeInstrumentID": self.instrument_id, "orderSide": self.position, "orderQuantity":int(self.total_lots * self.lot_size), "limitPrice": trigger_price, 'stopPrice':self.entry_price, 'orderUniqueIdentifier': self.leg_name})
            print(f"Order placed for {self.simple_momentum['direction']}  of value {sm_value} and entry price is {limit_price}")
            print(order)
        else:
            # self.freeze_quantity = int(self.df[[self.df.instrument_token]==self.instrument_id].FreezeQty.values[0])-1
            # if (int(self.lot_size) *self.total_lots) > self.freeze_quantity:
            #     valid_quantity_list = slice_orders(int(self.lot_size) *self.total_lots, self.freeze_quantity)
            #     for quantity in valid_quantity_list:
            #         order = self.xts.place_market_order({"exchangeInstrumentID": self.instrument_id, "orderSide": self.position,
            #                           "orderQuantity":quantity,"limitPrice":0,
            #                             "stopPrice": 1, "orderUniqueIdentifier": self.leg_name})
                    

            order = self.xts.place_market_order({"exchangeInstrumentID": self.instrument_id, "orderSide": self.position,
                                      "orderQuantity":int(self.lot_size) *self.total_lots,"limitPrice":0,
                                        "stopPrice": 1, "orderUniqueIdentifier": self.leg_name})
        # self.pegasus.log(order)
        self.publisher.add_trade_subscriber(self)
        self.publisher.add_subscriber(self, [self.instrument_id])

    def check_leg_conditions(self):
        pass
    
    async def leg_place_order(self):        
        # entry_price = self.market_data[-1:][0]['LastTradedPrice']
        print('leg place order invoked')
        print('waiting for the trade data to be set')
        await self.trade_data_event.wait()
        self.trade_data_event.clear()
        latest_trade = self.trade_data[-1:][0]
        # print(latest_trade)
        if latest_trade['OrderStatus']=='Filled':
            self.trade_entry_price = float(latest_trade['OrderAverageTradedPrice'])
            trade_side = latest_trade['OrderSide']
            traded_quantity = latest_trade['OrderQuantity']
            entry_timestmap = latest_trade['ExchangeTransactTime']
            entry_slippage = self.trade_entry_price - self.entry_price
            trade = {'symbol': self.instrument_id, 'entry_price': self.entry_price, 'trade_price': self.trade_entry_price,  'trade' : trade_side, 'quantity' : traded_quantity, 'timestamp': entry_timestmap, 'entry_slippage': round((self.entry_price - self.trade_entry_price), 2)}
            # print(f'instrument traded at avg price of {self.trade_entry_price}, side {trade_side},\n with quantity {traded_quantity} and executed at  {entry_timestmap} and slippage is {entry_slippage}')
            # print(trade)
        # print(f'placing SL order now for {self.leg_name} SL points {self.stop_loss}')
        if self.stop_loss[0].lower()=='points':
            self.stop_loss = self.stop_loss[1]
        elif self.stop_loss[0].lower() == 'percent':
            self.stop_loss = round(self.trade_entry_price*self.stoploss[1]/100, 2)
        if trade_side.upper() == 'BUY':
            self.trade_position = 'long'
            print('trade position is long')
            self.sl_price = self.trade_entry_price - self.stop_loss
            trigger_price = self.sl_price - self.trigger_tolerance
        else: 
            self.trade_position = 'short'
            print('trade position is short')
            self.sl_price = self.trade_entry_price + self.stop_loss
            trigger_price = self.sl_price + self.trigger_tolerance
        orderSide = 'BUY' if trade_side.upper() == 'SELL' else 'SELL'
        orderid = f"{self.leg_name}_sl"
        
        order =  self.xts.place_SL_order({"exchangeInstrumentID": self.instrument_id,
                                           "orderSide": orderSide, "orderQuantity":traded_quantity, "limitPrice": trigger_price, 'stopPrice':self.sl_price, 'orderUniqueIdentifier': orderid})
        # self.pegasus.log(order)
    def order_execution():
        pass
    
    # async def calculate_mtm(self):
    #     print(f'calculate_mtm for {self.leg_name}')
    #     quantity = self.lot_size*self.total_lots 
    #     print(f'entering calculate_mtm for {self.leg_name}')
    #     print('waiting for tick data')
    #     await self.market_data_event.wait()
    #     self.market_data_event.clear()
    #     print(f'trade position {self.trade_position} for {self.leg_name}')
    #     while (self.trade_position):

    #         current_ltp = self.market_data[-1:][0]['LastTradedPrice']
            
    #         if self.trade_position.lower()== 'long':
    #             self.pnl = round((current_ltp - self.trade_entry_price)*quantity, 2)
    #             if self.pnl > self.max_profit:
    #                 self.max_profit
    #             elif self.pnl < self.max_loss:
    #                 self.max_loss = self.pnl
    #             # print(f'current m2m for {self.leg_name} is {self.pnl} and cmp {current_ltp}')
    #         else :
    #             self.pnl = round((self.trade_entry_price - current_ltp )*quantity, 2)
    #             if self.pnl > self.max_profit:
    #                 self.max_profit
    #             elif self.pnl < self.max_loss:
    #                 self.max_loss = self.pnl
    #             # print(f'current m2m for {self.leg_name} is {self.pnl} and cmp {current_ltp}')
    #         await asyncio.sleep(1)
    #     self.strategy.total_pnl += self.pnl
    
    async def calculate_mtm(self):
        print(f'calculate_mtm for {self.leg_name}')
        quantity = self.lot_size*self.total_lots 
        print(f'entering calculate_mtm for {self.leg_name}')
        print('waiting for tick data')
        await self.market_data_event.wait()
        self.market_data_event.clear()
        print(f'trade position {self.trade_position} for {self.leg_name}')
        time_now = datetime.now()
        while self.strategy.exit_time > time_now:
            time_now = datetime.now()
            if  not self.trade_position:
                self.realised_pnl = self.realised_pnl + self.pnl
                self.pnl = 0
                # print(f'm2m  {self.leg_name} is {self.realised_pnl} and there is no position')
                
            else:
                current_ltp = self.market_data[-1:][0]['LastTradedPrice']
                if self.trade_position.lower()== 'long':
                    self.pnl = round((current_ltp - self.trade_entry_price)*quantity, 2) + self.realised_pnl
                    await self.stoploss_trail(current_ltp, "long")
                    await self.roll_strike_handler(current_ltp, "long")
                    # print(f'm2m  {self.leg_name} is {self.pnl}')
                    # if self.pnl > self.max_profit:
                    #     self.max_profit
                    # elif self.pnl < self.max_loss:
                    #     self.max_loss = self.pnl
                    # print(f'm2m  {self.leg_name} is {self.pnl} ')
                else :
                    self.pnl = round((self.trade_entry_price - current_ltp )*quantity, 2) + self.realised_pnl
                    await self.stoploss_trail(current_ltp, "short")
                    await self.roll_strike_handler(current_ltp, "short")
                    # print(f'm2m  {self.leg_name} is {self.pnl}')
                    # if self.pnl > self.max_profit:
                    #     self.max_profit
                    # elif self.pnl < self.max_loss:
                    #     self.max_loss = self.pnl
                    # print(f'm2m  {self.leg_name} is {self.pnl} ')
            await asyncio.sleep(3)
        # self.strategy.total_pnl += self.pnl
            
    async def roll_strike_handler(self,ltp, position):
            print('entering roll_strike handler')
            if self.roll_strike:
                if ((position=="long") and ((ltp-self.trade_entry_price)> self.roll_strike["roll_strike_value"])):
                    #square off existing order
                    #cancel trigger order
                    selected_option = self.expiry_df[self.expiry_df['instrument_token']== self.instrument_id]
                    selected_strike = int(selected_option.iloc[0].strike)
                    print(selected_strike)
                    selected_roll_strike = int(selected_strike - self.base*self.roll_strike["roll_level"])
                    roll_option_name = self.expiry_df[self.expiry_df['strike'].astype(int)== selected_roll_strike]
                    print(f"selected strike is {roll_option_name['tradingsymbol'].values[0]}")
                if ((position=="short") and ((self.trade_entry_price-ltp)> self.roll_strike["roll_strike_value"])):
                    #square off existing order
                    #cancel trigger order
                    selected_option = self.expiry_df[self.expiry_df['instrument_token']== self.instrument_id]
                    selected_strike = int(selected_option.iloc[0].strike)
                    print(selected_strike)
                    selected_roll_strike = int(selected_strike + self.base*self.roll_strike["roll_level"])
                    roll_option_name = self.expiry_df[self.expiry_df['strike'].astype(int)== selected_roll_strike] 
                    print(f"selected strike is {roll_option_name['tradingsymbol'].values[0]}")
                else:
                    print('no need to roll strike')
            




    