import re
import json
import pandas as pd
import os
from utils import get_atm_strike
import time
from typing import Any, List
from io import StringIO
from datetime import datetime, timedelta
from utils import error_handler, get_expiry_list
from utils import Logger,  save_df_with_date, process_minutewise_tradebook, round_to_tick, parse_roll_strike
from constants import NIFTY_LOT_SIZE, BANKNIFTY_LOT_SIZE, FINNIFTY_LOT_SIZE, SENSEX_LOT_SIZE, MIDCAPNIFTY_LOT_SIZE
import asyncio
import copy
class LegBuilder:
    """
        Initializes the LegBuilder class with various attributes necessary for building and managing option legs in a strategy.
        
        Parameters:
        leg_name (str): The name of the leg.
        strategy (Any): The strategy object to which this leg belongs.
        total_lots (int): The total number of lots. [positive int value]
        lot_size (int): The size of each lot. [positive int value]
        position (str): The position type, either 'buy' or 'sell'.
        option_type (str): The type of option, either 'CE' or 'PE'.
        expiry (str): The expiry type, either 'current', 'next_expiry', or 'monthly'.
        strike_selection_criteria (dict): Criteria for selecting the strike price.
        roll_strike (bool, dict): Whether to roll the strike price.
        new_strike_selection_criteria (dict): Criteria for selecting the new strike price to roll the strike
        stop_loss (tuple): The stop loss settings.
        trailing_sl (dict): The trailing stop loss settings.
        no_of_reentry (int): The number of reentries allowed.
        simple_momentum (bool, optional): Whether to use simple momentum strategy, default is False.
        range_breakout (bool, optional): Whether to use range breakout strategy, default is False.
    """
    @error_handler
    def __init__(self, leg_name: str, strategy: Any, total_lots: int, position: str, option_type: str, expiry: str, 
                 strike_selection_criteria: dict, roll_strike: Any, new_strike_selection_criteria: dict, stop_loss: tuple, 
                 trailing_sl: dict, no_of_reentry: int, simple_momentum: bool = False, range_breakout: bool = False) -> None:
        self.pegasus = Logger(f'{strategy.name}.txt')
        self.leg_name = leg_name
        self.strategy = strategy
        self.underlying_data = self.strategy.fut_data
        self.range_breakout = range_breakout
        self.total_lots = total_lots
        self.position = position
        self.stop_loss = stop_loss
        if not stop_loss:
            self.stop_loss = 2e10 
        self.entry = False
        self.option_type = option_type
        self.master_expiry_df = self.strategy.ce_expiry_df if self.option_type.upper() == 'CE' else self.strategy.pe_expiry_df
        self.no_of_reentry = no_of_reentry
        self.expiry = 0 if expiry == 'current' else (1 if expiry == 'next_expiry' else 2 if expiry == 'monthly' else None)
        self.trailing_sl = trailing_sl
        self.trail_sl =copy.deepcopy(self.trailing_sl)
        self.strike_selection_criteria = strike_selection_criteria
        # disabling new_strike_selection_criteria and roll strike for now 
        self.roll_strike = roll_strike 
        print(f"roll strike is {self.roll_strike} for {self.leg_name}")
        self.new_strike_selection_criteria = {'profit': self.roll_strike['roll_strike'], 'roll_strike_strike_type': self.roll_strike['roll_strike_strike_type'], 'roll_trailing_sl': self.roll_strike['roll_trailing_sl'] } if self.roll_strike else False  #new_strike_selection_criteria
        # print(f"{self.new_strike_selection_criteria} is the new_strike_selection_criteria")
        self.roll_strike_data = self.strategy.roll_strike_atm_data
        self.roll_strike_data['timestamp'] = pd.to_datetime(self.roll_strike_data['timestamp']) 
        self.simple_momentum = simple_momentum
        self.tradebook = pd.DataFrame(columns=['symbol', 'entry_price', 'entry_timestamp', 'exit_price', 'exit_timestamp', 'pnl', 'max_profit', 'max_loss'])
        self.lot_size = self.strategy.lot_size
        self.leg_validator()
        self.unable_to_trade_days = 0
        self.base_sl = 0
        self.position_roll_pnl = 0
        self.iteration = 1
        self.reentry_count = 0
        #strike gaps are 100 for banknifty, for nifty and  for finnifty 50
        self.base = 100 if self.strategy.index=='banknifty' else 50
        
    
            
    
    """
            Validates the leg parameters.
            
            Raises:
            ValueError: If any of the conditions are not satisfied.
    """
    @error_handler
    def leg_validator(self) -> None:
            if not re.match("^[a-zA-Z0-9_]*$", self.leg_name):
                raise ValueError("Leg name must be alphanumeric")
            
            if not isinstance(self.total_lots, int) or self.total_lots <= 0:
                raise ValueError("Total lots must be a positive integer")
            
            if not isinstance(self.lot_size, int) or self.lot_size <= 0:
                raise ValueError("Lot size must be a positive integer")
            
            if self.position not in ['buy', 'sell']:
                raise ValueError("Position must be either 'buy' or 'sell'")
            
            if self.option_type not in ['CE', 'PE']:
                raise ValueError("Option type must be either 'CE' or 'PE'")
            
            valid_expiries = ["current", "next_expiry", "monthly"]
            if self.expiry not in [0, 1, 2]:
                raise ValueError(f"Invalid expiry. Valid options are {valid_expiries}")
            
            if not isinstance(self.strike_selection_criteria, dict):
                raise ValueError("Strike selection criteria must be a dictionary")
            
            # if not isinstance(self.roll_strike, (bool, dict)):
            #     raise ValueError("Roll strike must be a boolean or dictionary")
            
            # if not isinstance(self.new_strike_selection_criteria, (dict, bool)):
            #     raise ValueError("New strike selection criteria must be a dictionary or bool")
            
            if not isinstance(self.stop_loss, (list, bool)) or len(self.stop_loss) != 2:
                raise ValueError("Stop loss must be a list with two elements")
            
            if not isinstance(self.trail_sl, (dict, bool)):
                raise ValueError("Trailing stop loss must be a dictionary or bool")
            
            if not isinstance(self.no_of_reentry, int) or self.no_of_reentry <0:
                raise ValueError("Number of reentries must be a non-negative integer")
            
            if not isinstance(self.simple_momentum, (dict, bool)):
                raise ValueError("Simple momentum must be a dict or bool")
            
            if not isinstance(self.range_breakout, (dict, bool)):
                raise ValueError("Range breakout must be a dict or bool")
            
    """
        Calculates the straddle premium along with straddle_width, atm_pct and atm_straddle_premium. based on the given choice and value.
        Parameters:
        choice (str): The choice for straddle premium calculation.
        choice_value (Any): The value for the chosen straddle premium calculation.
        current_day (datetime): The current day for which the premium is calculated.
    """
    @error_handler
    def straddle_premium(self, choice: str, choice_value: Any, current_day: datetime) -> None:
        if choice.lower() in ['straddle_width', 'atm_pct', 'atm_straddle_premium']:
            if choice.lower() in ['atm_straddle_premium', 'straddle_width']:
                print(f"strike is {self.strike}")
                print(f"current day is {current_day.date()}")
                ce_df = (self.strategy.ce_expiry_df[(self.strategy.ce_expiry_df['strike'] == self.strike) & 
                         (self.strategy.ce_expiry_df['timestamp'].dt.date == current_day.date())])
                pe_df = (self.strategy.pe_expiry_df[(self.strategy.pe_expiry_df['strike'] == self.strike) & 
                         (self.strategy.pe_expiry_df['timestamp'].dt.date == current_day.date())])
                expiry_list = list(set(ce_df.expiry))
                expiry_list.sort()
                current_expiry = expiry_list[0]
                ce_df = ce_df[ce_df['expiry'] == current_expiry]
                pe_df = pe_df[pe_df['expiry'] == current_expiry]
                merged_df = pd.merge(ce_df, pe_df, on='timestamp', suffixes=('_ce', '_pe'))

                self.combined_straddle_df = merged_df[['timestamp', 'open_ce', 'open_pe', 'symbol_ce']]
                self.combined_straddle_df['atm_straddle'] = self.combined_straddle_df['open_ce'] + self.combined_straddle_df['open_pe']
                print(f"current expiry is {current_expiry}")

                # print(self.combined_straddle_df)
                combined_premium = self.combined_straddle_df.iloc[0].atm_straddle
                if choice.lower() == "atm_straddle_premium":
                    premium = round(((combined_premium * choice_value) / 100), 2)
                    self.premium_symbol_df = self.expiry_df[self.expiry_df['timestamp'] == self.timestamp]
                    self.premium_symbol_df['premium_difference'] = abs(self.premium_symbol_df['open'] - premium)
                    self.premium_symbol_df = self.premium_symbol_df.sort_values(by='premium_difference')
                    self.option_symbol = self.premium_symbol_df.iloc[0].symbol
                    self.entry_price = self.premium_symbol_df.iloc[0].open
                    self.option_symbol_df = self.expiry_df[self.expiry_df['symbol'] == self.option_symbol]
                    print(self.option_symbol, self.entry_price, premium)
                if choice.lower() == "straddle_width":
                    self.expiry_df = self.expiry_df[self.expiry_df['timestamp'] >= self.timestamp]
                    if choice_value['atm_strike'] == '+':
                        selected_strike = self.strike + combined_premium * choice_value['input']
                        print(self.strike)
                        selected_strike = get_atm_strike(selected_strike, self.base)
                        print(f'selected strike is {selected_strike}')
                        self.strike = selected_strike
                        selected_option = self.expiry_df[self.expiry_df['strike'].astype(int) == self.strike].iloc[0]
                        self.entry_price = selected_option.open
                        self.option_symbol = selected_option.symbol
                        self.option_symbol_df = self.expiry_df[self.expiry_df['symbol'] == self.option_symbol]

                    if choice_value['atm_strike'] == '-':
                        selected_strike = self.strike - combined_premium * choice_value['input']
                        print(self.strike)
                        selected_strike = get_atm_strike(selected_strike, self.base)
                        print(f'selected strike is {selected_strike}')
                        self.strike = selected_strike
                        selected_option = self.expiry_df[self.expiry_df['strike'].astype(int) == self.strike].iloc[0]
                        self.instrument_id = int(selected_option.instrument_token)
                        print(selected_option.tradingsymbol)
                    pass
            elif choice.lower() == 'atm_pct':
                print(f"selected atm was {self.strike}")
                if choice_value['atm_strike'] == '+':
                    atm_points = choice_value['input'] * self.strike
                    self.strike = get_atm_strike(self.strike + atm_points, self.base)
                elif choice_value['atm_strike'] == '-':
                    atm_points = choice_value['input'] * self.strike
                    self.strike = get_atm_strike(self.strike - atm_points, self.base)
                print(f"new atm is {self.strike}")
                self.option_symbol_df = self.daily_expiry_df[(self.daily_expiry_df['strike'].astype(int) == self.strike)]
                selected_option = self.option_symbol_df.iloc[0]
                self.option_symbol = selected_option.symbol
                self.entry_price = selected_option.open
    """
        Records a trade in the tradebook.
        
        Parameters:
        symbol (str): The symbol of the option.
        entry_price (float): The entry price of the trade.
        entry_time (datetime): The entry time of the trade.
        exit_price (float): The exit price of the trade.
        exit_time (datetime): The exit time of the trade.
        pnl (float): The profit and loss of the trade.
        max_profit (float): The maximum profit during the trade.
        max_loss (float): The maximum loss during the trade.
    """
    @error_handler
    def record_tradebook(self, symbol: str, entry_price: float, entry_time: datetime, exit_price: float, exit_time: datetime, 
                         pnl: float, max_profit: float, max_loss: float) -> None:
        new_record = {
            'symbol': symbol,
            'entry_price': entry_price,
            'entry_timestamp': entry_time,
            'exit_price': exit_price,
            'exit_timestamp': exit_time,
            'pnl': pnl,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'sl': self.base_sl
        }
        new_record['tsl'] = round_to_tick(self.sl) if self.trail_sl else None
        # new_record['sl'].apply(round_to_tick)
        
        self.tradebook = self.tradebook._append(new_record, ignore_index=True)
    """
        Records minute-wise trade data.
        
        Parameters:
        symbol (str): The symbol of the option.
        timestamp (datetime): The timestamp of the trade.
        entry_price (float): The entry price of the trade.
        close (float): The closing price at the given timestamp.
        pnl (float): The profit and loss at the given timestamp.
    """

    @error_handler
    def record_minutewise_tradebook(self, symbol: str, timestamp: datetime, entry_price: float, close: float, pnl: float, remark: str) -> None:
        
        new_record = {
            'symbol': symbol,
            'timestamp': timestamp,
            'entry_price': entry_price,
            'close': round_to_tick(close),
            'pnl': round_to_tick(pnl),
            'remark' : remark   
        }
        self.minutewise_tradebook = self.minutewise_tradebook._append(new_record, ignore_index=True)

    """
        Tracks the stop loss, trail SL (if required)and roll strike for the leg and manages reentry if required.
    """
    # @error_handler
    def stoploss_tracker(self) -> None:
        if self.reentry_count == -100:
            return
        self.pegasus.log(f"debugging stoploss tracker iteration is {self.iteration}")
        self.iteration += 1 # Increment the iteration counter
        self.trail_sl = copy.deepcopy(self.trailing_sl)
        print(f"------------------------------ entry is {self.entry} for {self.option_symbol} and TSL {self.trail_sl} --------------------------------")
        self.pegasus.log(f"trailing sl constant before modification {self.trailing_sl}  @ {self.trade_entry_time} inside tracker")
        # self.minutewise_tradebook = pd.DataFrame(columns=['symbol', 'timestamp', 'entry_price', 'close', 'pnl']) #commented this line 19th
        max_loss = 10E10
        max_profit = -10E10
        # self.reentry_count = self.no_of_reentry-1
        while self.reentry_count > 0:
            if self.trail_sl:
                if self.trail_sl["trail_value_type"] =="percent":
                            if self.trail_sl['trail_type'] == "lock_and_trail":
                                self.trail_sl["lock_adjustment"]["priceMove"] = (self.entry_price*(self.trail_sl["lock_adjustment"]["priceMove"]/100))
                                self.trail_sl["lock_adjustment"]["sl_adjustment"] = (self.entry_price*(self.trail_sl["lock_adjustment"]["sl_adjustment"]/100))
                                self.trail_sl["lock_adjustment"]["trail_priceMove"] = (self.entry_price*(self.trail_sl["lock_adjustment"]["trail_priceMove"]/100))
                                self.trail_sl["lock_adjustment"]["trail_sl_adjustment"] = (self.entry_price*(self.trail_sl["lock_adjustment"]["trail_sl_adjustment"]/100))
                                self.trail_sl["trail_value_type"] ="points"
                                print(f"trail_sl after modification in stoploss tracker is {self.trail_sl} for {self.option_symbol} @ {self.trade_entry_time}")
                                self.pegasus.log(f"trail_sl after modification in stoploss tracker is {self.trail_sl} for {self.trailing_sl}  @ {self.trade_entry_time}")

                                self.pegasus.log(f"trail_sl is {self.trail_sl} for {self.option_symbol} @ {self.trade_entry_time}")
                            if self.trail_sl['trail_type'] =="lock":
                                self.trail_sl["priceMove"] = (self.entry_price*(self.trail_sl["priceMove"]/100))
                                self.trail_sl["sl_adjustment"] = (self.entry_price*(self.trail_sl["sl_adjustment"]/100))
                                self.trail_sl["trail_value_type"] ="points"
                                print(f"trail_sl is {self.trail_sl} for {self.option_symbol} @ {self.trade_entry_time}")
                                # self.pegasus.log(f"trail_sl after modification in stoploss tracker is {self.trail_sl} for {self.option_symbol} @ {self.trade_entry_time}")
                                self.pegasus.log(f"trail_sl after modification in stoploss tracker is {self.trail_sl} for {self.trailing_sl}  @ {self.trade_entry_time}")
            # point of discussion
            self.option_symbol_df = self.option_symbol_df[self.option_symbol_df['timestamp'] >= self.trade_entry_time]
            if self.entry and self.position.lower() == 'buy':
                for idx, row in self.option_symbol_df.iterrows():
                    points_pnl = row["close"] - self.entry_price
                    points_pnl = round_to_tick(points_pnl)
                    trail_pnl = row["high"] - self.entry_price
                    self.pnl = round_to_tick(points_pnl * (self.lot_size * self.total_lots))
                    if self.new_strike_selection_criteria:
                        roll_pnl =  round_to_tick(row["high"] - self.entry_price)
                        if roll_pnl >= self.new_strike_selection_criteria["profit"]:
                            print(f"rolling strike now because roll_pnl is {roll_pnl} and roll_profit is {self.new_strike_selection_criteria['profit']}")
                            self.pegasus.log(f"rolling strike now because roll_pnl is {roll_pnl} and roll_profit is {self.new_strike_selection_criteria['profit']}")
                            self.trade_exit_time = row["timestamp"]
                            round(self.entry_price + self.new_strike_selection_criteria["profit"],2)
                            max_profit = self.pnl
                            remark = "position_roll"
                            # print(f"-------closing position to roll {self.trade_exit_time}, {self.exit_price}-----")
                            self.record_minutewise_tradebook(self.option_symbol, row['timestamp'], self.entry_price, self.exit_price, self.new_strike_selection_criteria["profit"], remark)
                            self.pegasus.log("recording book inside new_criteria")
                            self.record_tradebook(self.option_symbol, self.entry_price, self.trade_entry_time, self.exit_price, self.trade_exit_time, self.pnl, max_profit, max_loss)
                            self.pegasus.log(f"{self.option_symbol}, {self.entry_price}, {self.trade_entry_time}, {self.exit_price}, {self.trade_exit_time}, {self.pnl}, {max_profit}, {max_loss}")
                            current_atm_strike = self.roll_strike_data[self.roll_strike_data['timestamp']==row['timestamp']].values[0]
                            self.pegasus.log(f"{row['timestmap']} and current atm strike is {current_atm_strike}")
                            if self.option_type.lower() == 'ce':
                                self.strike = self.strike + (parse_roll_strike(self.new_strike_selection_criteria["roll_strike"])-1)*self.base
                            else:
                                self.strike = self.strike - (parse_roll_strike(self.new_strike_selection_criteria["roll_strike"])+1)*self.base
                            print("new strike is ", self.strike)
                            self.option_symbol = self.option_symbol[:len(self.option_symbol) - 11] + str(self.strike) + self.option_symbol[len(self.option_symbol) - 6:]
                            self.option_symbol_df = self.daily_expiry_df[(self.daily_expiry_df["symbol"] == self.option_symbol) & 
                                                                         (self.daily_expiry_df["timestamp"] > self.trade_exit_time)]
                            # print(f"------------------{row['timestamp']}position getting rolled over----------------------")
                            if not self.option_symbol_df.empty:
                                self.entry_price = self.option_symbol_df.iloc[0].open
                                self.trade_entry_time = self.option_symbol_df.iloc[0].timestamp
                                self.sl_value = self.roll_strike['roll_stop_loss'][0]
                                self.sl = round_to_tick(round_to_tick(self.entry_price - self.sl_value))
                                print(f"rolled over position {self.trade_entry_time} {self.entry_price}, {self.sl} for {self.option_symbol}")
                                self.entry = True

                                self.stoploss_tracker()
                                break
                            else:
                                # print(f'{self.option_symbol} is not available for {row["timestamp"]}')
                                return

                        # print(f"trail adjusted from percent to points")
                    if self.trail_sl:
                        
                        if self.trail_sl["trail_type"] == "lock":
                            if trail_pnl >= self.trail_sl["priceMove"]:
                                trail_increment_factor = trail_pnl // self.trail_sl["priceMove"]
                                original_sl = round_to_tick(self.entry_price - self.sl_value)
                                updated_sl = round_to_tick(original_sl + trail_increment_factor * self.trail_sl["sl_adjustment"])
                                if updated_sl > self.sl:
                                    print(f"stoploss adjusted from {self.sl} to {updated_sl}")
                                    self.pegasus.log(f"stoploss adjusted from {self.sl} to {updated_sl} for symbol {self.option_symbol} @ {row['timestamp']}")
                                    self.sl = updated_sl
                                    # self.trail_sl = False
                        elif self.trail_sl["trail_type"] == "lock_and_trail":
                            
                            if (trail_pnl >= self.trail_sl["lock_adjustment"]["priceMove"]) and (not self.locked_trail):
                                # trail_increment_factor = trail_pnl -  self.trail_sl["lock_adjustment"]["priceMove"]
                                original_sl = round_to_tick(self.entry_price - self.sl_value)
                                updated_sl = round_to_tick(original_sl + self.trail_sl["lock_adjustment"]["sl_adjustment"])
                                if updated_sl > self.sl: 
                                    print(f"stoploss adjusted from {self.sl} to {updated_sl}")
                                    self.pegasus.log(f"stoploss adjusted from {self.sl} to {updated_sl} for symbol {self.option_symbol} @ {row['timestamp']}")
                                    self.sl = updated_sl
                                    # self.trail_sl["lock_adjustment"] = self.trail_sl["trail_adjustment"]
                                    self.locked_trail=True
                            if self.locked_trail:
                                if trail_pnl>= round_to_tick(self.trail_sl["lock_adjustment"]["trail_priceMove"] + self.trail_sl["lock_adjustment"]["priceMove"]):
                                    # trail_increment_factor = (trail_pnl - self.trail_sl["lock_adjustment"]["priceMove"]) //self.trail_sl["lock_adjustment"]["trail_sl_adjustment"]
                                    trail_increment_factor = (trail_pnl - self.trail_sl["lock_adjustment"]["priceMove"]) //self.trail_sl["lock_adjustment"]["trail_priceMove"]
                                    original_sl = round_to_tick(self.entry_price - self.sl_value)
                                    updated_sl = round_to_tick((original_sl + self.trail_sl["lock_adjustment"]["sl_adjustment"]) +  (trail_increment_factor*self.trail_sl["lock_adjustment"]["trail_sl_adjustment"]))
                                    # updated_sl = round_to_tick(original_sl + trail_increment_factor * self.trail_sl["lock_adjustment"]["trail_sl_adjustment"] + self.trail_sl["lock_adjustment"]["sl_adjustment"])
                                    if updated_sl > self.sl: 
                                        print(f"stoploss adjusted from {self.sl} to {updated_sl}")
                                        self.pegasus.log(f"stoploss adjusted from {self.sl} to {updated_sl} for symbol {self.option_symbol} @ {row['timestamp']} bcz {self.entry_price} to {row['low']}")
                                        self.sl = updated_sl
                    remark ="none"
                    self.record_minutewise_tradebook(self.option_symbol, row['timestamp'], self.entry_price, row['close'], self.pnl, remark)
                    if self.pnl <= max_loss:
                        max_loss = self.pnl
                    if self.pnl >= max_profit:
                        max_profit = self.pnl
                    if row['low'] <= self.sl:
                        self.entry = False
                        self.exit_price = self.sl
                        self.trade_exit_time = row['timestamp']
                        self.pnl = round_to_tick(self.sl - self.entry_price) * (self.lot_size * self.total_lots)
                        # print(f"SL hit for the position at {row['timestamp']}, exiting leg {self.leg_name} and current pnl for the leg is {self.pnl}")
                        self.pegasus.log(f"SL hit for the position at {row['timestamp']}, exiting leg {self.leg_name} and current pnl for the leg is {self.pnl}")
                        max_loss = self.pnl
                        self.pegasus.log(f"recording book inside row < sl")
                        self.record_tradebook(self.option_symbol, self.entry_price, self.trade_entry_time, self.exit_price, self.trade_exit_time, self.pnl, max_profit, max_loss)
                        self.pegasus.log(f"{self.option_symbol}, {self.entry_price}, {self.trade_entry_time}, {self.exit_price}, {self.trade_exit_time}, {self.pnl}, {max_profit}, {max_loss}")
                        remark = "sl_hit"
                        self.tradebook.loc[self.tradebook.index[-1], 'remark'] = remark
                        self.locked_trail = False
                        self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'pnl'] = self.pnl
                        self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'remark'] = remark
                        self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'close'] = self.sl
                        self.reentry_count -= 1
                        # note for devveloper : exit time can be entry_time as well, hence added '>=' else keep '>'
                        self.option_symbol_df = self.option_symbol_df[self.option_symbol_df['timestamp'] >= self.trade_exit_time] 
                        break
                if not self.entry:
                    self.wait_for_reentry(self.option_symbol_df, self.entry_price)
                    continue
            elif self.entry and self.position.lower() == "sell":
                for idx, row in self.option_symbol_df.iterrows():
                    points_pnl = (self.entry_price - row["close"])
                    trail_pnl = (self.entry_price - row["low"])
                    self.pnl = points_pnl * (self.lot_size * self.total_lots) + self.position_roll_pnl #+ self.combined_sl_pnl
                    if self.new_strike_selection_criteria:
                        roll_pnl = round_to_tick(self.entry_price - row["low"])
                        if roll_pnl >= self.new_strike_selection_criteria["profit"]:
                            print(f"roll_pnl is {roll_pnl} and {self.new_strike_selection_criteria['profit']} is roll_strike_pnl_criteria")
                            self.trade_exit_time = row["timestamp"]
                            self.exit_price = round(self.entry_price - self.new_strike_selection_criteria["profit"],2)
                            max_profit = self.pnl
                            remark = "position_roll"
                            print(f"rolling strike now because roll_pnl is {roll_pnl} and roll_profit is {self.new_strike_selection_criteria['profit']}")
                            self.pegasus.log(f"rolling strike now because roll_pnl is {roll_pnl} and roll_profit is {self.new_strike_selection_criteria['profit']}")
                            print(f"-------closing position to roll {self.trade_exit_time}, {self.exit_price}-----")
                            self.pegasus.log(f"-------closing position to roll {self.trade_exit_time}, {self.exit_price}-----")
                            remark = "position_roll"
                            pnl = (self.entry_price - self.exit_price) * (self.lot_size * self.total_lots) + self.position_roll_pnl
                            self.record_minutewise_tradebook(self.option_symbol, row['timestamp'], self.entry_price, self.exit_price, pnl, remark)
                            self.pegasus.log(f"recording book inside new strike selection")
                            self.record_tradebook(self.option_symbol, self.entry_price, self.trade_entry_time, self.exit_price, self.trade_exit_time, pnl, max_profit, max_loss)
                            self.pegasus.log(f"for {self.option_symbol}, entry price {self.entry_price}, entry time was {self.trade_entry_time}, exit price is {self.exit_price}, exit time is {self.trade_exit_time}, current p&l {self.pnl}, max_profit {max_profit} and max loss is {max_loss}")
                            # self.pnl = self.pnl + (roll_pnl)*(self.lot_size * self.total_lots) #added this line on 17th oct for roll_strike
                            # max_profit = self.pnl
                            self.position_roll_pnl = round(self.position_roll_pnl + (self.new_strike_selection_criteria["profit"]*(self.lot_size * self.total_lots)),2)
                            print(f"previous strike is {self.strike}")
                            current_atm_strike = self.roll_strike_data[self.roll_strike_data['timestamp']==row['timestamp']].iloc[0]['atm']
                            self.pegasus.log(f"{row['timestamp']} and current atm strike is {current_atm_strike}")

                            self.strike = parse_roll_strike(self.new_strike_selection_criteria["roll_strike_strike_type"], self.option_type, current_atm_strike, self.base)
                            # print("new strike is ", self.strike)
                            self.pegasus.log(f"new strike is {self.strike} for {self.option_symbol} @ {row['timestamp']} ")
                            self.option_symbol = self.option_symbol[:len(self.option_symbol) - 11] + str(self.strike) + self.option_symbol[len(self.option_symbol) - 6:]
                            # self.pegasus.log(f"new option_symbol is {self.option_symbol} @ {row['timestamp']}")
                            self.option_symbol_df = self.daily_expiry_df[(self.daily_expiry_df["symbol"] == self.option_symbol) & 
                                                                         (self.daily_expiry_df["timestamp"] > self.trade_exit_time)]
                            if not self.option_symbol_df.empty:
                                self.entry_price = self.option_symbol_df.iloc[0].open
                                self.trade_entry_time = self.option_symbol_df.iloc[0].timestamp
                                if self.roll_strike['roll_stop_loss'][1]!='points':
                                    self.sl_value = (self.roll_strike['roll_stop_loss'][0]*self.entry_price)/100
                                else:
                                    self.sl_value = self.roll_strike['roll_stop_loss'][0]
                                self.sl = self.entry_price + self.sl_value
                                self.base_sl = self.sl.copy() #added on 18th oct for roll_strike
                                print(f"rolled over position {self.trade_entry_time} {self.entry_price}, {self.sl} for {self.option_symbol}")
                                self.pegasus.log(f"rolled over position {self.trade_entry_time} {self.entry_price}, {self.sl} for {self.option_symbol}")
                                self.entry = True
                            
                                self.pegasus.log(f"rolling strike tsl was {self.trailing_sl} ")
                                self.trailing_sl = self.new_strike_selection_criteria['roll_trailing_sl'] #added new code on 17th oct
                                self.pegasus.log(f"roll strike tsl is updated as {self.trailing_sl} for {self.option_symbol} @ {self.entry_price}")
                                self.stoploss_tracker()
                                break
                            else:
                                print(f'{self.option_symbol} is not available for {row["timestamp"]}')
                                return
                    if self.trail_sl:
                        if self.trail_sl["trail_type"] == "lock":
                            if trail_pnl >= self.trail_sl["priceMove"]:
                                trail_increment_factor = trail_pnl // self.trail_sl["priceMove"]
                                original_sl = self.entry_price + self.sl_value
                                updated_sl = original_sl - trail_increment_factor * self.trail_sl["sl_adjustment"]
                                if updated_sl < self.sl:
                                    print(f"stoploss adjusted from {self.sl} to {updated_sl} @ {row['timestamp']}")
                                    self.pegasus.log(f"stoploss adjusted from {self.sl} to {updated_sl} for symbol {self.option_symbol} @ {row['timestamp']} bcz {self.entry_price} to {row['low']}")
                                    self.sl = updated_sl
                                    # self.trail_sl = False
                        elif self.trail_sl["trail_type"] == "lock_and_trail":
                                if (trail_pnl >= self.trail_sl["lock_adjustment"]["priceMove"]) and (not self.locked_trail):
                                    print(trail_pnl, self.trail_sl["lock_adjustment"]["priceMove"])
                                    # trail_increment_factor = trail_pnl  - self.trail_sl["lock_adjustment"]["priceMove"]
                                    original_sl = self.entry_price + self.sl_value
                                    updated_sl = original_sl - self.trail_sl["lock_adjustment"]["sl_adjustment"]
                                    if updated_sl < self.sl: 
                                        print(f"stoploss adjusted from {self.sl} to {updated_sl}")
                                        self.pegasus.log(f"stoploss adjusted from {self.sl} to {updated_sl} for symbol {self.option_symbol} @ {row['timestamp']}")
                                        self.sl = updated_sl
                                        # self.trail_sl["lock_adjustment"] = self.trail_sl["trail_adjustment"]
                                        self.locked_trail=True
                                if self.locked_trail:
                                    if trail_pnl>= (self.trail_sl["lock_adjustment"]["trail_priceMove"] + self.trail_sl["lock_adjustment"]["priceMove"]):
                                        trail_increment_factor = (trail_pnl - self.trail_sl["lock_adjustment"]["priceMove"]) //self.trail_sl["lock_adjustment"]["trail_priceMove"]
                                        # self.pegasus.log(f"trail_increment_factor is  {trail_increment_factor} @{row['timestamp']}")
                                        original_sl = round_to_tick(self.entry_price + self.sl_value)
                                        updated_sl = round_to_tick((original_sl - self.trail_sl["lock_adjustment"]["sl_adjustment"]) -  (trail_increment_factor*self.trail_sl["lock_adjustment"]["trail_sl_adjustment"]))
                                        if updated_sl < self.sl: 
                                            print(f"stoploss adjusted from {self.sl} to {updated_sl}")
                                            self.pegasus.log(f"stoploss adjusted from {self.sl} to {updated_sl} for symbol {self.option_symbol} @ {row['timestamp']} bcz {self.entry_price} to {row['low']}")
                                            self.sl = updated_sl

                                # if points_pnl >= self.trail_sl["lock_adjustment"]["priceMove"]:
                                #     trail_increment_factor = points_pnl // self.trail_sl["lock_adjustment"]["priceMove"]  
                                #     original_sl = self.entry_price + self.sl_value
                                #     updated_sl = original_sl - trail_increment_factor * self.trail_sl["lock_adjustment"]["sl_adjustment"]
                                #     if updated_sl < self.sl:
                                #         # print(f"stoploss adjusted from {self.sl} to {updated_sl}")
                                #         self.sl = updated_sl
                                #         self.trail_sl["lock_adjustment"] = self.trail_sl["trail_adjustment"]
                    remark ="none"
                    self.record_minutewise_tradebook(self.option_symbol, row['timestamp'], self.entry_price, row['close'], self.pnl, remark)
                    if self.pnl <= max_loss:
                        max_loss = self.pnl
                    if self.pnl >= max_profit:
                        max_profit = self.pnl
                    if row['high'] >= self.sl:
                        self.entry = False
                        self.exit_price = self.sl
                        self.trade_exit_time = row['timestamp']
                        self.reentry_count -= 1
                        self.pnl = (self.entry_price - self.sl) * (self.total_lots * self.lot_size)
                        # self.combined_sl_pnl = self.combined_sl_pnl + (self.entry_price - self.sl) * (self.total_lots * self.lot_size) #added on 21st oct for combined sl pnl

                        # print(f"SL hit for the position at {row['timestamp']}, exiting leg {self.leg_name} and current pnl for the leg is {self.pnl}")
                        if max_loss < self.pnl:
                            max_loss = self.pnl
                        self.pegasus.log(f"recording tradebook in high > sl")
                        self.record_tradebook(self.option_symbol, self.entry_price, self.trade_entry_time, self.exit_price, self.trade_exit_time, self.pnl, max_profit, max_loss)
                        self.pegasus.log(f"sl hit for {self.option_symbol}, entry {self.entry_price}, {self.trade_entry_time}, exit {self.exit_price}, {self.trade_exit_time}, {self.pnl}, {max_profit}, {max_loss} and base sl is {self.base_sl}")
                        remark="sl_hit"
                        self.tradebook.loc[self.tradebook.index[-1], 'remark'] = remark
                        self.locked_trail=False
                        # self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'pnl'] = self.pnl #+ self.position_roll_pnl #added position_roll_pnl on 19th oct
                        self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'pnl'] = self.pnl + self.position_roll_pnl #added position_roll_pnl on 19th oct
                        self.pegasus.log(f"pnl is {self.pnl} and minutewise_pnl is {self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'pnl']} for timestamp {self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'timestamp']}")
                        self.position_roll_pnl = 0
                        self.pegasus.log(f"position_roll_pnl reset to 0 as the sl got hit @ {self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'timestamp']}") #added line on 22nd oct
                        self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'remark'] = remark
                        self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'close'] = self.sl
                        self.option_symbol_df = self.option_symbol_df[self.option_symbol_df['timestamp'] > self.trade_exit_time]
                        
                        # self.pegasus.log(f"reentry updated due to sl getting hit {self.reentry_count}")
                        break
                if not self.entry:
                    # self.position_roll_pnl = self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'pnl'] #21st oct
                    # self.pegasus.log(f"position roll pnl is {self.position_roll_pnl}")
                    self.wait_for_reentry(self.option_symbol_df, self.entry_price)
                    continue
            if self.entry:
                self.entry = False
                self.exit_price = row['open']
                self.trade_exit_time = row['timestamp']
                self.pnl = (row['open'] - self.entry_price) * (self.lot_size * self.total_lots) if self.position.lower() == 'buy' else (self.entry_price - row['open']) * (self.lot_size * self.total_lots)
                self.record_tradebook(self.option_symbol, self.entry_price, self.trade_entry_time, self.exit_price, self.trade_exit_time, self.pnl, max_profit, max_loss)
                self.pegasus.log(f"recording book here in self entry block {self.option_symbol}, {self.entry_price}, {self.trade_entry_time}, {self.exit_price}, {self.trade_exit_time}, {self.pnl}, {max_profit}, {max_loss}")
                self.tradebook.loc[self.tradebook.index[-1], 'remark'] = "market closed"
                self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'remark'] = "market closed"
                self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'close'] = self.exit_price
                self.reentry_count = self.no_of_reentry - 100
                if self.position.lower() =='buy':
                    minutewise_pnl = self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-2], 'pnl'] + (row['open'] - self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-2], 'close'] ) * (self.lot_size * self.total_lots) 
                else:
                    minutewise_pnl = self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-2], 'pnl'] + (self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-2], 'close'] - row['open']) * (self.lot_size * self.total_lots)
                self.minutewise_tradebook.loc[self.minutewise_tradebook.index[-1], 'pnl'] = minutewise_pnl
                # print(f"---No SL hit for {self.leg_name}, at {row['timestamp']} close is {row['close']} and total pnl is {self.pnl}---")
                self.pegasus.log(f"---No SL hit for {self.leg_name}, at {row['timestamp']} open is {row['open']} and total pnl is {self.pnl}, market closed---")
                self.reentry_count = -100
                break #added on 21st oct
                # return #data not found was resolved using return
            else:
                # print(self.minutewise_tradebook)
                break

        # print(self.minutewise_tradebook)
        df = process_minutewise_tradebook(self.minutewise_tradebook, self.strategy.entry_time, self.strategy.exit_time, self.lot_size * self.total_lots)
        save_df_with_date(df, row['timestamp'], self.leg_name, self.strategy.name)
     
    
    """ 
        Waits for a reentry based on the provided data and entry price.
        
        Parameters:
        df (pd.DataFrame): The dataframe containing option data.
        entry_price (float): The entry price for reentry.
    """
    def wait_for_reentry(self, df: pd.DataFrame, entry_price: float) -> None: 
        # if  self.new_strike_selection_criteria:
        #     pass
        # else:

        # check this function once the roll_strike method is implemented #implemented on 17th Oct
        # if not self.new_strike_selection_criteria:
        if self.reentry_count >= 0:
            for idx, row in df.iterrows():
                if row['timestamp'] < pd.Timestamp(self.end_timestamp):
                    if (self.position.lower() == 'buy' and row['high'] >= entry_price and row['open'] < row['close']) or (self.position.lower() == 'sell' and row['low'] <= entry_price and row['open'] > row['close']):
                        self.sl = self.entry_price - self.sl_value if self.position.lower() == 'buy' else self.entry_price + self.sl_value
                        self.entry = True
                        self.trade_entry_time = row['timestamp']
                        # print(f'reentry{self.reentry_count} with {self.entry_price} and sl {self.sl} {self.sl_value}')
                        self.pegasus.log(f'reentrycount {self.reentry_count} with {self.entry_price} and sl {self.sl} @ {self.trade_entry_time} ')
                        break
                else:
                    self.pegasus.log(f"Skipping trade as row timestamp {row['timestamp']} is past end timestamp {self.end_timestamp}")


    """
        Fetches options symbol for the leg based on the condition provided in the LegBuilder class.
        And backtest them for provided period of time
    """                
    @error_handler
    async def backtest_selection(self) -> None:
        print('inside backtest selection method')
        async def process_backtest_daywise(idx, row):
            try:
                self.position_roll_pnl = 0
                self.entry = False
                self.reentry_count = self.no_of_reentry
                self.strike = row["atm"]
                self.combined_sl_pnl = 0
                self.locked_trail = False
                self.timestamp = row["timestamp"]
                date_part = self.timestamp.date()
                exit_timestamp = datetime.strptime(self.strategy.exit_time, '%H:%M:%S').time()
                self.end_timestamp = datetime.combine(date_part, exit_timestamp)
                self.expiry_df = self.master_expiry_df[(self.master_expiry_df['timestamp'] >= self.timestamp) & (self.master_expiry_df['timestamp'] <= self.end_timestamp)]
                print('------------------------expiry df----------------------')
                current_expiry, next_expiry, monthly_expiry = get_expiry_list(self.expiry_df)
                # print(current_expiry, next_expiry, monthly_expiry, row["timestamp"])
                if self.expiry == 0:
                    self.expiry_list = current_expiry
                elif self.expiry == 1:
                    self.expiry_list = next_expiry
                else:
                    self.expiry_list = monthly_expiry
                self.expiry_df = self.expiry_df[self.expiry_df['expiry'] == self.expiry_list]
                choice = self.strike_selection_criteria['strike_selection']
                choice_value = self.strike_selection_criteria['value']
                self.daily_expiry_df = self.expiry_df[(self.expiry_df['timestamp'] >= self.timestamp) & (self.expiry_df['timestamp'] <= self.end_timestamp)]
                self.daily_expiry_df = self.daily_expiry_df.sort_values(by='timestamp')
                self.straddle_premium(choice, choice_value, self.timestamp)

                if choice == 'strike':
                    if choice_value == 'ATM':
                        self.option_symbol_df = self.daily_expiry_df[(self.daily_expiry_df['strike'].astype(int) == self.strike)]
                        self.option_symbol = self.option_symbol_df.iloc[0].symbol
                        self.entry_price = self.option_symbol_df.iloc[0].open
                    elif choice_value.startswith('ITM'):
                        itm_depth = re.findall(r'\d+', choice_value)
                        if itm_depth:
                            if self.option_type == 'CE':
                                self.strike = self.strike - self.base * int(itm_depth[0])
                                self.option_symbol_df = self.daily_expiry_df[(self.daily_expiry_df['strike'].astype(int) == self.strike)]
                                self.option_symbol = self.option_symbol_df.iloc[0].symbol
                                self.entry_price = self.option_symbol_df.iloc[0].open
                            else:
                                self.strike = self.strike + self.base * int(itm_depth[0])
                                self.option_symbol_df = self.daily_expiry_df[(self.daily_expiry_df['strike'].astype(int) == self.strike)]
                                self.option_symbol = self.option_symbol_df.iloc[0].symbol
                                self.entry_price = self.option_symbol_df.iloc[0].open
                    elif choice_value.startswith('OTM'):
                        itm_depth = re.findall(r'\d+', choice_value)
                        if itm_depth:
                            if self.option_type == 'CE':
                                self.strike = self.strike + self.base * int(itm_depth[0])
                                self.option_symbol_df = self.daily_expiry_df[(self.daily_expiry_df['strike'].astype(int) == self.strike)]
                                self.option_symbol = self.option_symbol_df.iloc[0].symbol
                                self.entry_price = self.option_symbol_df.iloc[0].open
                            else:
                                self.strike = self.strike - self.base * int(itm_depth[0])
                                self.option_symbol_df = self.daily_expiry_df[(self.daily_expiry_df['strike'].astype(int) == self.strike)]
                                self.option_symbol = self.option_symbol_df.iloc[0].symbol
                                self.entry_price = self.option_symbol_df.iloc[0].open

                elif choice.lower() == 'closest_premium':
                    premium = choice_value
                    self.premium_symbol_df = self.expiry_df[self.expiry_df['timestamp'] == self.timestamp]
                    self.premium_symbol_df['premium_difference'] = abs(self.premium_symbol_df['open'] - premium)
                    self.premium_symbol_df = self.premium_symbol_df.sort_values(by='premium_difference')
                    self.option_symbol = self.premium_symbol_df.iloc[0].symbol
                    self.entry_price = self.premium_symbol_df.iloc[0].open
                    self.option_symbol_df = self.expiry_df[self.expiry_df['symbol'] == self.option_symbol]
                elif choice.lower() in ['straddle_width', 'atm_pct', 'atm_straddle_premium']:
                    pass
                if self.range_breakout:
                    timeframe = self.range_breakout['timeframe']
                    start_time = self.strategy.entry_time
                    range_time = self.timestamp + timedelta(minutes=timeframe)
                    self.range_symbol_df = self.option_symbol_df[self.option_symbol_df["timestamp"] < range_time]
                    self.range_symbol_df.set_index('timestamp', inplace=True)

                    resample_cols = ['open', 'high', 'low', 'close']
                    range_period = timeframe
                    resampled_df = self.range_symbol_df[resample_cols].resample(f'{range_period}T').agg({
                        'open': 'first',
                        'high': 'max',
                        'low': 'min',
                        'close': 'last',
                    })
                    self.range_high = resampled_df.iloc[0].high
                    self.range_low = resampled_df.iloc[0].low
                    # print(f"end time is {range_time}")
                    self.option_symbol_df = self.option_symbol_df[self.option_symbol_df["timestamp"] >= range_time]
                    for idx, row in self.option_symbol_df.iterrows():
                        if self.range_breakout["direction"] == "high":
                            if row["high"] >= self.range_high:
                                self.entry_price = self.range_high
                                self.trade_entry_time = row["timestamp"]
                                self.entry = True
                                break
                        else:
                            if row["low"] <= self.range_low:
                                self.entry_price = self.range_low
                                self.trade_entry_time = row["timestamp"]
                                self.entry = True

                if self.simple_momentum:
                    if self.simple_momentum["value_type"].lower() == "points":
                        sm_value = self.simple_momentum["value"]
                    else:
                        sm_value = self.entry_price * (self.simple_momentum["value"] / 100)
                        self.pegasus.log(f"sm_value is {sm_value}")
                    if self.simple_momentum['direction'].lower() == 'increment':
                        entry_criteria = self.entry_price + sm_value
                        self.pegasus.log(f"entry_criteria is {entry_criteria}")
                    elif self.simple_momentum['direction'].lower() == 'decay':
                        entry_criteria = self.entry_price - sm_value
                        self.pegasus.log(f"entry_criteria is {entry_criteria}")
                    self.option_symbol_df = self.option_symbol_df.sort_values(by='timestamp')
                    for idx, row in self.option_symbol_df.iterrows():
                        if self.simple_momentum['direction'].lower() == 'decay':
                            if row['low'] <= entry_criteria:
                                self.entry = True
                                self.entry_price = entry_criteria
                                self.trade_entry_time = row['timestamp']
                                print(f"entry for simple momentum @ {self.entry_price} as {row['low']} is lower than entry, {self.trade_entry_time}")
                                self.pegasus.log(f"entry for simple momentum @ {self.entry_price} as {row['low']} is lower than entry, {self.trade_entry_time}")
                                break
                        if self.simple_momentum['direction'].lower() == 'increment':
                            if row['high'] >= entry_criteria:
                                self.entry = True
                                self.entry_price = entry_criteria
                                self.trade_entry_time = row['timestamp']
                                print(f"entry for simple momentum @ {self.entry_price} as {row['high']} is higher than entry, {self.trade_entry_time}")
                                self.pegasus.log(f"entry for simple momentum @ {self.entry_price} as {row['high']} is higher than entry, {self.trade_entry_time}")
                                break

                self.option_symbol_df = self.option_symbol_df.sort_values(by='timestamp')
                print(f"debug entry at #691 is {self.entry} for symbol {self.option_symbol}")
                if not (self.range_breakout or self.simple_momentum):
                    print(f"simple momentum is not true for {self.option_symbol}")
                    self.entry = True
                if self.entry:
                    if self.stop_loss[0].lower() == 'points':
                        if self.position.lower() == 'buy':
                            self.sl_value = self.stop_loss[1]
                            self.sl = round_to_tick(self.entry_price - self.stop_loss[1])
                            self.base_sl = self.sl
                        else:
                            self.sl_value = self.stop_loss[1]
                            self.sl = round_to_tick(self.entry_price + self.stop_loss[1])
                            self.base_sl = self.sl
                        self.entry = True
                    if self.stop_loss[0].lower() == 'percent':
                        if self.position.lower() == 'buy':
                            self.sl_value = (self.entry_price * self.stop_loss[1]) / 100
                            self.sl = round_to_tick(self.entry_price - self.sl_value)
                            self.base_sl = self.sl
                        else:
                            self.sl_value = (self.entry_price * self.stop_loss[1]) / 100
                            self.sl = self.entry_price + self.sl_value
                            self.base_sl = self.sl
                        self.entry = True
                    print(f"{self.entry_price}, {self.sl}, {self.sl_value} @ {row['timestamp']} for {self.option_symbol} and entry is {self.entry}")
                    if not (self.range_breakout or self.simple_momentum):
                        self.trade_entry_time = self.timestamp 
                        self.option_symbol_df = self.option_symbol_df[(self.option_symbol_df['timestamp'] >= self.timestamp) & 
                                                                    (self.option_symbol_df['timestamp'] <= self.end_timestamp)]
                    self.pegasus.log(f"trail_sl is {self.trail_sl} and original tsl is {self.trailing_sl} for this block")
                    self.minutewise_tradebook = pd.DataFrame(columns=['symbol', 'timestamp', 'entry_price', 'close', 'pnl']) #added 19th oct
                    self.stoploss_tracker()
                    self.pegasus.log(f"stoploss tracker ends here for sure @ {row['timestamp']} ")
            except Exception as e:
                print(f"data not found for {row['timestamp']}  {e}")
                self.pegasus.log(f"data not found for {row['timestamp']} {self.option_symbol}  {e}")
                self.unable_to_trade_days = self.unable_to_trade_days + 1
        
        tasks = [process_backtest_daywise(idx, row) for idx, row in self.underlying_data.iterrows()]
        self.tradebook.sort_values('entry_timestamp', inplace=True)
        await asyncio.gather(*tasks)
        file_path = f"{self.strategy.name}\{self.leg_name}_combined_pnl.csv"
        self.tradebook['trade_side'] = self.position
        self.tradebook['exit_price'] = self.tradebook['exit_price'].apply(round_to_tick)
        self.tradebook['quantity'] = self.lot_size*self.total_lots
        self.tradebook.to_csv(file_path, index=False)
        print(f"tradebook saved in {file_path}")
        self.tradebook.to_csv("sonu.csv",index=False)







        # strategy_folder_name = f"{self.strategy.name}"
        # if not os.path.exists(strategy_folder_name):
        #     os.makedirs(strategy_folder_name)
        # self.tradebook.to_csv(os.path.join(strategy_folder_name, f"{strategy_folder_name}_final.csv"), index=False)
