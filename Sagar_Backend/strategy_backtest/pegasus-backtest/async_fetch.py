import asyncio
import pandas as pd
import aiosqlite
import concurrent.futures
import matplotlib.pyplot as plt
from typing import Any, Dict, List
from analyzer.analyzer import Analyzer
from datetime import datetime
from data.data import fetch_data, fetch_data_and_filter
from opt_strategy.moving_average import process_group, evaluate_strategy, moving_crossover_strategy
DataFrame = pd.DataFrame
Queue = asyncio.Queue



async def main() -> None:
    """
    main function.
    """
    start_date = '2021-01-01'
    end_date = '2021-12-30'
    symbol = 'NIFTY'

    queue = asyncio.Queue()
    fetch_task = asyncio.create_task(fetch_data_and_filter(start_date, end_date, symbol, queue))
    evaluate_task = asyncio.create_task(evaluate_strategy(queue,symbol))    
    await asyncio.gather(fetch_task)
    await asyncio.gather(evaluate_task)
    tradebook_path = 'tradebook.csv'
    analyzer = Analyzer(tradebook_path)
    df = pd.read_csv(tradebook_path)
    analyzer.plot_data()
    daily_returns_df = pd.read_csv('daily_returns.csv')

    ohlc_data_df = pd.read_csv('daily_ohlc.csv', usecols=['date', 'open', 'high', 'low', 'close'])

    merged_df = pd.merge(daily_returns_df, ohlc_data_df, on='date', how='left')
    print(merged_df)
    merged_df.to_csv('daily_returns.csv',index=False)
asyncio.run(main())
