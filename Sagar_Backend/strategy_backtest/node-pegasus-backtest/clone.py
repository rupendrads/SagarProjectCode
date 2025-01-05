import sys
import json
import pandas as pd
from analyzer.analyzer import Analyzer
from data.data import fetch_futures_data, fetch_options_data
from opt_strategy.moving_average import evaluate_strategy, new_moving_average
from typing import Any, Dict, List
from datetime import datetime
from strategy.strategy import Strategy
from optimizer.optimizer import Optimizer
import warnings
warnings.filterwarnings("ignore")
import time
def run_backtest_moving_strategy(data,strategy : Strategy) -> None:
    """
    Function to run backtest with moving average strategy.
    """
    new_moving_average(data,strategy)

# Read input data from standard input
input_data = sys.stdin.read()

# Parse the JSON string to retrieve the combination and data
try:
    input_dict = json.loads(input_data)
    combination = input_dict['combination']
    data = input_dict['data']
    df = pd.DataFrame(data)
except json.JSONDecodeError as e:
    print("Error parsing input JSON:", e)
    sys.exit(1)

# Your further processing with combination and data goes here
# Example:
strat_kwargs = dict(combination)
strat_kwargs['strat_name'] = 'moving_average'
strat_kwargs['start_date'] = '2021-01-01'
strat_kwargs['end_date'] = '2021-12-30'
strat_kwargs['instrument'] = 'NIFTY'
strat_kwargs['is_intraday'] = True
strat_kwargs['trade_lot'] = 5
strat_kwargs['broker_charges']=20
strat_kwargs['capital'] = 2500000
strat_kwargs['lot_size'] = 50 # if nifty, it will be 50, else for banknifty its 15 (current lot_size)
strat_kwargs['slippage']  = 0
strat_kwargs['stop_loss']=20
strategy = Strategy(**strat_kwargs)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
run_backtest_moving_strategy(df, strategy)