import asyncio
import pandas as pd
import aiosqlite
import concurrent.futures
import matplotlib.pyplot as plt
from typing import Any, Dict, List

# Define types for function parameters and return values
DataFrame = pd.DataFrame
Queue = asyncio.Queue

def process_group(date: str, group: DataFrame, short_window: int, long_window: int) -> List[Dict[str, Any]]:
    """
    Process each group of data within the specified date range.

    Parameters:
        date (str): The date of the group.
        group (DataFrame): A group of data for the specified date.
        short_window (int): The short moving average window.
        long_window (int): The long moving average window.

    Returns:
        List[Dict[str, Any]]: List of tradebook dictionaries.
    """
    tradebook = []
    stop_loss = 20
    exit_time = pd.Timestamp(year=group['timestamp'].iloc[0].year,
                             month=group['timestamp'].iloc[0].month,
                             day=group['timestamp'].iloc[0].day,
                             hour=15,
                             minute=0)
    in_trade = False
    entry_time = None
    entry_price = None
    pnl = 0
    trades_per_day = 0
    
    for index, row in group.iterrows():
        if row['timestamp'].time() >= pd.Timestamp('09:20').time():
            if not in_trade and row['short_ma'] > row['long_ma']:
                in_trade = True
                entry_time = row['timestamp']
                entry_price = row['close']
                trades_per_day += 1
            elif in_trade and (row['timestamp'] == exit_time or row['short_ma'] < row['long_ma'] or row['close'] < entry_price - stop_loss):
                in_trade = False
                exit_time = row['timestamp']
                exit_price = row['close']
                pnl = exit_price - entry_price
                tradebook.append({'entry_time': entry_time,
                                  'exit_time': exit_time,
                                  'entry_price': entry_price,
                                  'exit_price': exit_price,
                                  'pnl': pnl,
                                  'trades_per_day': trades_per_day})
    return tradebook

async def fetch_data(start_date: str, end_date: str, symbol: str, conn: aiosqlite.Connection, queue: Queue) -> None:
    """
    Fetch data from the database within the specified date range.

    Parameters:
        start_date (str): Start date of the data to fetch.
        end_date (str): End date of the data to fetch.
        symbol (str): Symbol or instrument to fetch data for.
        conn (aiosqlite.Connection): SQLite database connection.
        queue (asyncio.Queue): Queue to store data.
    """
    print(f'Fetching data from {start_date} to {end_date}')
    
    start_year = pd.Timestamp(start_date).year
    end_year = pd.Timestamp(end_date).year
    
    data = []
    
    for year in range(start_year, end_year + 1):
        table_name = f'{symbol}_{year}'
        query = f'''
                SELECT *
                FROM {table_name}
                WHERE timestamp BETWEEN ? AND ?
                AND type = 'FUT'
                '''
        async with conn.execute(query, (start_date, end_date)) as cursor:
            year_data = await cursor.fetchall()
        data.extend(year_data)
    
    await queue.put(data)
    print('Fetching done')

async def fetch_data_and_filter(start_date: str, end_date: str, symbol: str, queue: Queue) -> None:
    """
    Fetch data for the specified date range, and put it into the queue for further processing.

    Parameters:
        start_date (str): Start date of the data to fetch.
        end_date (str): End date of the data to fetch.
        symbol (str): Symbol or instrument to fetch data for.
        queue (asyncio.Queue): Queue to store data.
    """
    try:
        conn = await aiosqlite.connect(r'C:\Users\pegas\OneDrive\Desktop\zip data\index_data.db')
        
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        interval_size = len(date_range) // 10    #interval size
        for i in range(0, len(date_range), interval_size):
            interval_start = date_range[i]
            if i + interval_size < len(date_range):
                interval_end = date_range[i + interval_size]
            else:
                interval_end = date_range[-1]
            
            await fetch_data(interval_start.strftime('%Y-%m-%d'), interval_end.strftime('%Y-%m-%d'), symbol, conn, queue)
        
        await conn.close()
        await queue.put(None)
    except Exception as e:
        print(f'Error occurred while fetching data: {e}')
        
 

def moving_crossover_strategy(df: DataFrame, short_window: int = 50, long_window: int = 200) -> DataFrame:
    """
    Apply moving crossover strategy to the DataFrame.

    Parameters:
        df (DataFrame): Input DataFrame containing OHLC data.
        short_window (int): The short moving average window.
        long_window (int): The long moving average window.

    Returns:
        DataFrame: Tradebook containing trade details.
    """
    df['short_ma'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_ma'] = df['close'].rolling(window=long_window, min_periods=1).mean()

    grouped = df.groupby(df['timestamp'].dt.date)
    tradebooks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_group = {executor.submit(process_group, date, group, short_window, long_window): (date, group) for date, group in grouped}
        for future in concurrent.futures.as_completed(future_to_group):
            date, group = future_to_group[future]
            try:
                tradebooks.append(future.result())
            except Exception as exc:
                print(f"Exception occurred for date {date}: {exc}")
    return pd.DataFrame([trade for trades in tradebooks for trade in trades])


async def evaluate_strategy(queue: Queue, symbol : str) -> None:
    """
    Evaluate the strategy using  data from the queue.

    Parameters:
        queue (asyncio.Queue): Queue containing  data.
    """
    tradebooks = []
    while True:
        data = await queue.get()
        if data is None:  
            print("Received None, breaking the loop")  
            break
        if data:  
            df = pd.DataFrame(data)
            column_names = ["id", "timestamp", "symbol", "expiry", "type", "strike", "open", "high", "low", "close", "oi", "volume", "provider", "upload_time"]
            df.columns = column_names
            df = df[df['symbol'] == f'{symbol}-I.NFO']
            df = df[['timestamp', 'symbol', 'open' , 'high' , 'low', 'close']]
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.sort_values(by='timestamp', inplace=True)
            df.reset_index(inplace=True, drop=True)
            print(df)
            tradebook = moving_crossover_strategy(df, 5, 11)
            tradebooks.append(tradebook)
        queue.task_done()
    if tradebooks:
        collective_tradebook = pd.concat(tradebooks, ignore_index=True)
        cumulative_pnl = collective_tradebook['pnl'].cumsum()
        
        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(collective_tradebook['exit_time'], cumulative_pnl)
        plt.xlabel('Time')
        plt.ylabel('Cumulative PnL')
        plt.title('Cumulative PnL Over Time')
        plt.grid(True)
        plt.savefig(f'cumulative_pnl.png')
        collective_tradebook.to_csv('ma_strategy.csv',index=False)
        print(collective_tradebook)

async def main() -> None:
    """
    main function.
    """
    start_date = '2020-01-01'
    end_date = '2021-12-30'
    symbol = 'NIFTY'

    queue = asyncio.Queue()
    fetch_task = asyncio.create_task(fetch_data_and_filter(start_date, end_date, symbol, queue))
    evaluate_task = asyncio.create_task(evaluate_strategy(queue,symbol))    
    await asyncio.gather(fetch_task)
    await asyncio.gather(evaluate_task)
    
# Run the main function
asyncio.run(main())
