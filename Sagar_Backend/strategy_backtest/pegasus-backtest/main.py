import asyncio
import pandas as pd
from analyzer.analyzer import Analyzer
from data.data import fetch_data
from opt_strategy.moving_average import evaluate_strategy, new_moving_average
from typing import Any, Dict, List
from datetime import datetime
from strategy.strategy import Strategy
from optimizer.optimizer import Optimizer
import warnings
warnings.filterwarnings("ignore")
import time
import concurrent.futures

def run_backtest_moving_strategy(data,strategy : Strategy) -> None:
    """
    Function to run backtest with moving average strategy.
    """
    new_moving_average(data,strategy)

def main() -> None:
    time_before_calculation = datetime.now()
    print(time_before_calculation)
    """
    main function.
    """
    params_json = '''
    {
        "start_time": {"default_value": "09:30", "min_time": "09:30", "max_time": "10:00", "difference": 15},
        "end_time": {"default_value": "13:30", "min_time": "13:30", "max_time": "15:00", "difference": 15},
        "short_ma": {"period_name": "ShortPeriod", "default_value": 10, "min_value": 3, "max_value": 20, "increment": 1},
        "long_ma": {"period_name": "LongPeriod", "default_value": 15, "min_value": 5, "max_value": 50, "increment": 1},
        "timeframe": {"default_value": 5, "min_value": 5, "max_value": 30, "increment": 1},
        "rule": {"parameter_list": ["short_ma", "long_ma"], "relation": "3 <= long_ma - short_ma < 7"},
        "stop_loss" : {"default_value": 20, "min_value": 20, "max_value": 30, "increment": 1},
        "moving_average":{"default_value":"ema", "types" :["sma","ema","dema"]}
    }
    '''


    start_date = '2021-01-01'
    end_date = '2021-12-30'
    instrument = 'NIFTY'
    data =  fetch_data(start_date, end_date, instrument)
    optimizer = Optimizer(params_json,True)
    combinations = optimizer.generate_final_combination_list()
    combination_size = len(combinations)
    combinations = combinations[:500]
    print(datetime.now())
    print(f'{combination_size} combinations generated, which will take approximately {combination_size/6} minutes to finish')
    choice = int(input(f'press 1 to proceed, 0 to quit:'))
    if choice:
        batch_size = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = []
            for i in range(0, len(combinations), batch_size):
                batch_combinations = combinations[i:i + batch_size]
                for combination in batch_combinations:
                    print(combination)
                    strat_kwargs = dict(combination)
                    strat_kwargs['strat_name'] = 'moving_average'
                    strat_kwargs['instrument'] = 'NIFTY'
                    # strat_kwargs['is_intraday'] = True
                    strategy = Strategy(**strat_kwargs)
                    futures.append(executor.submit(run_backtest_moving_strategy, data, strategy))

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()  
                except Exception as e:
                    print(f'Exception occurred: {e}')
    print(datetime.now())
main()

# def main() -> None:
#     time_before_calculation = datetime.now()
#     print(time_before_calculation)
#     """
#     main function.
#     """
#     params_json = '''
#     {
#         "start_time": {"default_value": "09:30", "min_time": "09:30", "max_time": "10:00", "difference": 15},
#         "end_time": {"default_value": "13:30", "min_time": "13:30", "max_time": "15:00", "difference": 15},
#         "short_ma": {"period_name": "ShortPeriod", "default_value": 10, "min_value": 3, "max_value": 20, "increment": 1},
#         "long_ma": {"period_name": "LongPeriod", "default_value": 15, "min_value": 5, "max_value": 50, "increment": 1},
#         "timeframe": {"default_value": 5, "min_value": 5, "max_value": 30, "increment": 1},
#         "rule": {"parameter_list": ["short_ma", "long_ma"], "relation": "3 <= long_ma - short_ma < 7"},
#         "moving_average":{"default_value":"sma", "types" :["sma","ema"]},
#         "stop_loss" : {"default_value": 20, "min_value": 20, "max_value": 30, "increment": 1}
#     }
#     '''


#     # combinations= combinations
#     start_date = '2021-01-01'
#     end_date = '2021-12-30'
#     instrument = 'NIFTY'
#     # print(combinations)
#     data =  fetch_data(start_date, end_date, instrument)
#     optimizer = Optimizer(params_json,False)
#     combinations = optimizer.generate_final_combination_list()
#     combination_size = len(combinations)
#     print(f'{combination_size} combinations generated, which will take approximately {combination_size/6} minutes to finish')
#     choice = int(input(f'press 1 to proceed, 0 to quit:'))
#     if choice:
#         # print(combinations)
#         # time.sleep(5)
#         counter = 0
#         for combination in combinations:
#             counter+=1
#             strat_kwargs = dict(combination)
#             strat_kwargs['strat_name'] = 'moving_average'
#             strat_kwargs['instrument'] = 'NIFTY'
#             strat_kwargs['is_intraday'] = True
#             strategy = Strategy(**strat_kwargs)
#             # strategy.display_parameters()
#             run_backtest_moving_strategy(data,strategy)
# main()