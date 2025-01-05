import json
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any
import pandas as pd
from utils import get_atm_strike, process_minutewise_tradebook, assign_index, error_handler
import asyncio
from data import get_underlying_ltp, get_expiry_df, filter_dataframe_by_time
import sys
from datetime import datetime
from typing import List, Any
from constants import *
import os
import shutil
class Strategy:
    """
        Initializes the Strategy class with various attributes necessary for the trading strategy.
        
        Parameters:
        name (str): The name of the strategy.
        index (str): The index on which the strategy is based. (NIFTY BANK, NIFTY 50, NIFTY FIN SERVICE)
        underlying (str): The underlying asset of the strategy. (SPOT, FUTURES, IMPLIED_FUTURES)
        strategy_type (str): The type of the strategy. (INTRADAY, BTST, POSITIONAL)
        start_date (datetime): The start date of the strategy. (2021-04-04, YYYY-MM-DD)
        end_date (datetime): The end date of the strategy. (2021-05-04, YYYY-MM-DD)
        entry_time (datetime): The time at which the strategy enters a position. (09:30:00, HH:MM:SS , note : cant be before 09:15)
        last_entry_time (datetime): The latest time at which the strategy can enter a position.(15:30:00, HH:MM:SS, note : cant be after 15:30)
        exit_time (datetime): The time at which the strategy exits a position. (15:30:00, HH:MM:SS, note : cant be after 15:30)
        square_off (float): The square off value for the strategy. (COMPLETE, PARTIAL)
        overall_sl (float): The overall stop-loss value for the strategy. (NON NEGATIVE FLOAT VALUE)
        overall_target (float): The overall target value for the strategy.(NON NEGATIVE FLOAT VALUE)
        trailing_for_strategy (float): The trailing stop value for the strategy. []
        implied_futures_expiry (str, optional): The futures expiry type, default is 'current'. [current, monthly]
        brokerage (int, optional) : brokerage charged by broker per lot, default is 20
        """
    @error_handler
    def __init__(self, name: str, index: str, underlying: str, strategy_type: str, start_date: datetime, end_date: datetime, 
                 entry_time: datetime, last_entry_time: datetime, exit_time: datetime, square_off: float, 
                 overall_sl: float, overall_target: float, trailing_for_strategy: float, underlying_data: pd.DataFrame, options_data : pd.DataFrame,  implied_futures_expiry: str = 'current', optimization_flag: bool=False, brokerage: int = 20) -> None:
        
        self.name = name
        self.index = index.upper()
        print(f"index of strategy is {self.index}")
        self.start_date = start_date
        self.end_date = end_date
        self.underlying = underlying
        self.implied_futures_expiry = implied_futures_expiry
        self.strategy_type = strategy_type
        self.entry_time = entry_time
        self.last_entry_time = last_entry_time
        self.exit_time = exit_time
        self.square_off = square_off
        self.overall_sl = overall_sl
        self.overall_target = overall_target
        self.trailing_for_strategy = trailing_for_strategy
        self.legs: List[Any] = []
        self.trail_count = 0
        self.lot_sizes_list = self.load_lot_sizes()
        self.get_base_value()
        self.total_pnl = 0
        self.trail_flag = False
        self.strategy_validator()
        self.implied_futures_expiry = 0 if implied_futures_expiry.lower() == 'current' else 1 if implied_futures_expiry.lower() == 'next' else False
        # self.index = assign_index(index)
        self.assign_lot_size()
        print(f"start time is {self.entry_time}")
        self.roll_strike_atm_data = underlying_data
        self.roll_strike_atm_data['atm'] = self.roll_strike_atm_data.apply(lambda row: get_atm_strike(row['close'], self.base), axis=1)
        print(f"roll strike atm data is {self.roll_strike_atm_data}")
        self.fut_data = filter_dataframe_by_time(underlying_data, self.entry_time)
        self.expiry_df = options_data
        # self.fut_data = get_underlying_ltp(self.index, self.entry_time, start_date, end_date,self.underlying, self.implied_futures_expiry)
        # self.fut_data = get_underlying_ltp()
        # self.expiry_df = get_expiry_df(self.index, self.start_date, self.end_date, self.entry_time, self.exit_time)
        self.ce_expiry_df = self.expiry_df[self.expiry_df['type'] == 'CE']
        self.pe_expiry_df = self.expiry_df[self.expiry_df['type'] == 'PE']
        self.fut_data['atm'] = self.fut_data.apply(lambda row: get_atm_strike(row['close'], self.base), axis=1)
        self.optimization_flag= optimization_flag
        print(f"optimization_flag is {self.optimization_flag}")
        if os.path.exists(self.name):
            shutil.rmtree(self.name)
        os.makedirs(self.name)
        self.fut_data.to_csv(os.path.join(self.name, f'{self.name}_fut_data.csv'), index=False)
        self.ce_expiry_df.to_csv(os.path.join(self.name, f'{self.name}_ce_expiry_df.csv'), index=False)
        self.pe_expiry_df.to_csv(os.path.join(self.name, f'{self.name}_pe_expiry_df.csv'), index=False)
        print(self.fut_data)
        self.brokerage_charge = brokerage
    @error_handler
    def load_lot_sizes(self):
        self.json_file = "lot_sizes.json"
        try:
            with open(self.json_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: The file {self.json_file} was not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: The JSON file could not be decoded.")
            return {}
    @error_handler
    def assign_lot_size(self):
        self.lot_size = self.lot_sizes_list.get(str(self.index.upper()), None)
    
    """
        Validates the strategy parameters.
        
        Raises:
        ValueError: If any of the conditions are not satisfied.
    """
    @error_handler
    def get_base_value(self) -> None:
        if self.index == "NIFTY":
            self.base = NIFTY_BASE
        elif self.index == "BANKNIFTY":
            self.base = BANKNIFTY_BASE
        elif self.index == "FINNIFTY":
            self.base = FINNIFTY_BASE
        elif self.index == "MIDCPNIFTY":
            self.base = MIDCAPNIFTY_BASE
        elif self.index =="SENSEX":
            self.base = SENSEX_BASE
        else:
            print(f"Unknown base: {self.base}")
            raise ValueError("base couldnt be determined")
    # def get_base_value(self) -> None:
    #     if self.index == "NIFTY 50":
    #         self.base = NIFTY_BASE
    #     elif self.index == "NIFTY BANK":
    #         self.base = BANKNIFTY_BASE
    #     elif self.index == "NIFTY FIN SERVICE":
    #         self.base = FINNIFTY_BASE
    #     elif self.index == "MIDCAPNIFTY":
    #         self.base = MIDCAPNIFTY_BASE
    #     elif self.index =="SENSEX":
    #         self.base = SENSEX_BASE
    #     else:
    #         print(f"Unknown base: {self.base}")
    #         raise ValueError("base couldnt be determined")
    @error_handler
    def strategy_validator(self) -> None:
        if not re.match("^[a-zA-Z0-9_]*$", self.name):
            raise ValueError("Name must be alphanumeric")
        
        # valid_indices = ["NIFTY BANK", "NIFTY 50", "NIFTY FIN SERVICE"]
        # if self.index.upper() not in valid_indices:
        #     raise ValueError(f"Invalid index. Valid options are {valid_indices}")
        valid_underlying =["spot", "futures", "implied_futures"]
        if self.underlying.lower() not in valid_underlying:
            raise ValueError(f"Invalid underlying. Valid options are {valid_underlying}")
        
        try:
            datetime.strptime(self.entry_time, TIMEFORMAT)
        except ValueError:
            raise ValueError("Entry time must be in HH:MM:SS format")
        
        try:
            datetime.strptime(self.last_entry_time, TIMEFORMAT)
        except ValueError:
            raise ValueError("Last entry time must be in HH:MM:SS format")
        
        try:
            datetime.strptime(self.exit_time, TIMEFORMAT)
        except ValueError:
            raise ValueError("Exit time must be in HH:MM:SS format")
        
        if self.square_off.upper() not in ["COMPLETE", "PARTIAL"]:
            raise ValueError("Square off must be either 'COMPLETE' or 'PARTIAL'")
        
        if not isinstance(self.overall_sl, (int, float)) or self.overall_sl < 0:
            raise ValueError("Overall stop-loss must be a non-negative float")
        
        if not isinstance(self.overall_target, (int, float)) or self.overall_target < 0:
            raise ValueError("Overall target must be a non-negative float")
        
        if not isinstance(self.trailing_for_strategy, (dict, bool)):
            raise ValueError("Trailing stop value must be a dictionary or False")
        
        date_format = "%Y-%m-%d"
        try:
            start_date_obj = datetime.strptime(self.start_date, date_format)
            if start_date_obj > datetime.now() - timedelta(days=1):
                raise ValueError("Start date cannot be in the future or today's date")
        except ValueError:
            raise ValueError("Start date must be in YYYY-MM-DD format")
        
        try:
            end_date_obj = datetime.strptime(self.end_date, date_format)
            if end_date_obj < start_date_obj:
                raise ValueError("End date must be greater than start date")
            if end_date_obj > datetime.now():
                raise ValueError("End date cannot be in the future")
        except ValueError:
            raise ValueError("End date must be in YYYY-MM-DD format")
        
        valid_expiries = ["current", "monthly", False]
        if self.implied_futures_expiry not in valid_expiries:
            raise ValueError(f"Invalid implied futures expiry. Valid options are {valid_expiries}")


    """
        Processes the minute-wise tradebook for each leg in the provided list of legs.
        
        Parameters:
        legs_list (List[Any]): A list of legs where each leg contains minute-wise tradebook data.

        Returns:
        None
    """
    @error_handler
    def combined_legs(self, legs_list: List[Any]) -> None:
        for leg in legs_list:
            process_minutewise_tradebook(leg.minutewise_tradebook, self.entry_time, self.exit_time)
    

    """
        Converts a timestamp string to a datetime object.
        
        Parameters:
        timestamp (str): The timestamp string to be converted.
        
        Returns:
        datetime: The corresponding datetime object.
    """
    @error_handler
    def convert_to_datetime(self, timestamp: str) -> datetime:
        today_date = datetime.now().date()
        formatted_time = f"{today_date} {timestamp}:00"
        return datetime.strptime(formatted_time, '%Y-%m-%d %H:%M:%S')
