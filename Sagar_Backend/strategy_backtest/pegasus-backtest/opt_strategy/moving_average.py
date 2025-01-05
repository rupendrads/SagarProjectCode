import asyncio
import pandas as pd
import aiosqlite
import concurrent.futures
import matplotlib.pyplot as plt
from typing import Any, Dict, List
from analyzer.analyzer import Analyzer
from datetime import datetime
import inspect
import sys
import numpy as np
sys.path.append('C:\\Users\\pegas\\OneDrive\\Desktop\\pegasus-backtest-new\\helpers')
from helpers.technicals import TechnicalIndicators
DataFrame = pd.DataFrame
Queue = asyncio.Queue
import os

def update_performance_file(performance_data):
    csv_file = 'performance.csv'

    if os.path.isfile(csv_file):
        existing_df = pd.read_csv(csv_file)
    else:
        existing_df = pd.DataFrame(columns=['start_time', 'end_time', 
            'short_ma', 'long_ma', 'timeframe', 'stop_loss', 'moving_average',
            'total_trades', 'winning_trades', 'losing_trades', 'net_profit', 
            'winning_strike', 'avg_profit', 'avg_loss', 'total_brokerage', 
            'max_dd_percentage', 'max_winning_streak', 'max_losing_streak', 
            'days_in_dd', 'max_drawdown', 'cagr', 'exposure', 'fund_required'
        ])

    updated_df = pd.concat([existing_df, pd.DataFrame(performance_data, index=[0])], ignore_index=True)
    updated_df.to_csv(csv_file, index=False)
def resample_ohlc_df(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    Resamples OHLC Dataframe of 1 minute to given timeframe
    Args:
        df(pd.Dataframe): input dataframe
        timeframe(str): timeframe to resample data(1min, 5min, 15min, 30min, 60min, D)
    Returns:
        pd.DataFrame: returns resampled dataframe
    """
    try:
        df_copy = df.copy(deep=True)
        df = df_copy
        df["day"] = df.apply(lambda x: x.timestamp.date(), axis=1)
        df.set_index("timestamp", inplace=True)
        day_groups = df.groupby("day")
        resampled_dfs = []
        for day, day_df in day_groups:
            start_time = f'{day} 09:15:00'
            end_time = f'{day} 15:29:00'
            dt_index = pd.date_range(start=start_time, end=end_time, freq='1min')
            df_range = pd.DataFrame(index=dt_index)
            df_range = df_range.rename_axis("timestamp")
            df_range = df_range.merge(day_df, how='left', left_index=True, right_index=True)
            # df_range.fillna(method='ffill', inplace=True)
            resample_cols = {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last"
            }
            if "volume" in df_range.columns:
                resample_cols["volume"] = "sum"
            resampled_df = df_range.resample(timeframe, origin="start").agg(resample_cols)
            resampled_df.reset_index(inplace=True)
            # resampled_df.fillna(method='ffill', inplace=True)
            resampled_dfs.append(resampled_df)
        combined_df = pd.concat(resampled_dfs, ignore_index=True)
        return combined_df
    except Exception as e:
        print(f"Error occurred while resampling OHLC df [{df}: {str(e)}]")
        return pd.DataFrame()


def trade_analysis(df,lot_size,brokerage):
    total_trades = len(df)
    winning_trades = len(df[df.pnl >= 0])
    losing_trades = len(df[df.pnl < 0])
    net_profit = round(sum(df['pnl']),2)
    winning_strike = round(winning_trades / losing_trades if losing_trades != 0 else 0,2)  
    avg_profit = round(sum(df[df.pnl >= 0].pnl) / total_trades, 2)
    avg_loss = round(sum(df[df.pnl < 0].pnl) / total_trades,2)  
    total_brokerage = round(total_trades * brokerage)
    return total_trades, winning_trades, losing_trades, net_profit, winning_strike, avg_profit, avg_loss, total_brokerage


def calculate_streaks(series):
    streak_count = 0
    max_streak = 0
    for value in series:
        if value > 0:
            streak_count += 1
            max_streak = max(max_streak, streak_count)
        else:
            streak_count = 0
    return max_streak
def calculate_cagr(initial_capital, net_pnl):
    ending_value = initial_capital + net_pnl
    number_of_years = 1
    
    cagr = (ending_value / initial_capital) ** (1 / number_of_years) - 1
    return cagr*100

def new_moving_average(data, strategy):
    metrices = []
    tradebooks = []
    if data:
        df = pd.DataFrame(data)
        column_names = ["id", "timestamp", "symbol", "expiry", "type", "strike", "open", "high", "low", "close", "oi", "volume", "provider", "upload_time","implied_futures_weekly","implied_futures_monthly"]
        df.columns = column_names
        # print(df)
        df = df[df['symbol'] == f'{strategy.instrument}-I.NFO']
        implied_futures = df[['timestamp','implied_futures_weekly', 'implied_futures_monthly']]
        implied_futures['timestamp'] = pd.to_datetime(implied_futures['timestamp'])
        df = df[['timestamp', 'symbol', 'open' , 'high' , 'low', 'close']]
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values(by='timestamp', inplace=True)
        df.reset_index(inplace=True, drop=True)
        timeframe_value = f'{strategy.timeframe}min'
        df = resample_ohlc_df(df,timeframe_value)
        df = pd.merge(df, implied_futures, on='timestamp', how='left')
        # Compute short and long moving averages
        average_calculator = TechnicalIndicators(df)
        # print(strategy.moving_average, strategy.short_ma, strategy.long_ma)
        df['short_ma'] =average_calculator.calculate_indicator(indicator_type=strategy.moving_average,window= strategy.short_ma) #df['close'].rolling(window=strategy.short_ma, min_periods=1).mean()
        df['long_ma'] = average_calculator.calculate_indicator(indicator_type=strategy.moving_average,window=strategy.long_ma)#df['close'].rolling(window=strategy.long_ma, min_periods=1).mean()
        df.dropna(inplace=True)
        stop_loss = strategy.stop_loss
        
        # Group by day
        grouped_df = df.groupby(pd.Grouper(key='timestamp', freq='D'))
        for day, daily_data in grouped_df:
            in_trade = False
            entry_time = None
            entry_price = None
            pnl = 0
            tradebook = []
            for idx, row in daily_data.iterrows():
                try:
                    trades_per_day = 0
                    end_time_component = strategy.end_time.split(':')
                    end_time = pd.Timestamp(year=daily_data['timestamp'].iloc[0].year,
                                    month=daily_data['timestamp'].iloc[0].month,
                                    day=daily_data['timestamp'].iloc[0].day,
                                    hour=int(end_time_component[0]),
                                    minute=int(end_time_component[1]))
                    if row['timestamp'].time() >= pd.Timestamp(strategy.start_time).time():
                        if not in_trade and row['short_ma'] > row['long_ma'] and row['timestamp'] < end_time:
                            in_trade = True
                            entry_time = row['timestamp']
                            entry_price = row['implied_futures_weekly']
                            trades_per_day += 1
                        elif in_trade and ((row['timestamp'] >= end_time) or (row['short_ma'] < row['long_ma']) or (row['implied_futures_weekly'] < (entry_price - stop_loss))):
                            in_trade = False
                            exit_time = row['timestamp']
                            exit_price = row['implied_futures_weekly']
                            pnl = round((exit_price - entry_price), 2)
                            tradebook.append({'entry_time': entry_time,
                                            'exit_time': exit_time,
                                            'entry_price': entry_price,
                                            'exit_price': exit_price,
                                            'pnl': pnl,
                                            'trades_per_day': trades_per_day})
                except:
                    print(f'error occured for day {day}')
                    continue
            # print(tradebook)
            tradebooks.append(tradebook)
    collective_tradebook = pd.concat([pd.DataFrame(tb) for tb in tradebooks], ignore_index=True)
    collective_tradebook = collective_tradebook.sort_values('entry_time')
    collective_tradebook.to_csv(f'./strategy/moving_average/{strategy.strat_name}_{strategy.instrument}_{strategy.start_time.replace(":", "")}_{strategy.end_time.replace(":", "")}_{strategy.short_ma}_{strategy.long_ma}_{strategy.timeframe}_{strategy.stop_loss}_{strategy.moving_average}tradebook.csv',index=False)
    data = []
    capital = 200000
    lot_size = 50
    collective_tradebook['date'] = collective_tradebook['entry_time'].dt.date
    tradebook_grp = collective_tradebook.groupby('date')
    for date, grp in tradebook_grp:
            day_pnl = grp['pnl'].sum()
            data.append({'date': date, 'pnl': day_pnl})
    daily_pnl = pd.DataFrame(data)
    daily_returns_df = daily_pnl.copy()
    daily_returns_df.pnl = daily_returns_df.pnl * lot_size
    daily_returns_df["pnl_pct"] = (daily_returns_df["pnl"] / capital) * 100
    daily_returns_df.to_csv('daily_returns.csv')
    daily_returns = daily_returns_df.copy()
    daily_returns['date'] = daily_returns['date']#.dt.date
    daily_pnl = daily_returns.groupby('date')['pnl'].sum().reset_index()
    daily_returns_df.reset_index(inplace=True, drop=True)
    daily_returns_df["pnl_pct_cumulative"] = daily_returns_df["pnl_pct"].cumsum()
    cumulative_pnl = np.cumsum(daily_returns_df['pnl'])
    max_cumulative_pnl = np.maximum.accumulate(cumulative_pnl)
    daily_returns_df["drawdown"] = ((cumulative_pnl / max_cumulative_pnl) - 1) * 100
    days_in_drawdowon = len(daily_returns_df[daily_returns_df['drawdown']<0])
    max_winning_streak = calculate_streaks(daily_returns_df['pnl'])
    max_losing_streak = calculate_streaks(-daily_returns_df['pnl'])
    daily_returns_df.to_csv('deepak.csv',index=False)
    daily_returns_df.set_index("date", inplace=True,drop=True)
    # max_drawdown_days = consecutive_lengths.max() if not consecutive_lengths.empty else 0
    
    # print("Max number of days in drawdown:", max_drawdown_days)

    max_drawdown = daily_returns_df['drawdown'].min()
    max_dd_percentage = abs((int(max_drawdown)*lot_size*100)/capital)
    total_trades, winning_trades, losing_trades, net_profit, winning_strike, avg_profit, avg_loss, total_brokerage = trade_analysis(collective_tradebook,50, 40)
    cagr = calculate_cagr(capital, (cumulative_pnl-total_brokerage))
    exposure = 125000*50/lot_size
    performance_data = {
    'start_time':strategy.start_time, 
    'end_time':strategy.end_time, 
    'short_ma':strategy.short_ma,
    'long_ma':strategy.long_ma,
    'timeframe':strategy.timeframe,
    'stop_loss':strategy.stop_loss, 
    'moving_average':strategy.moving_average,
    'total_trades': total_trades,
    'winning_trades': winning_trades,
    'losing_trades': losing_trades,
    'net_profit': net_profit,
    'winning_strike': winning_strike,
    'avg_profit': avg_profit,
    'avg_loss': avg_loss,
    'total_brokerage': total_brokerage,
    'max_dd_percentage': max_dd_percentage,
    'max_winning_streak': max_winning_streak,
    'max_losing_streak': max_losing_streak,
    'days_in_dd': days_in_drawdowon,
    'max_drawdown': round(max_drawdown,2)*lot_size,
    'cagr': cagr,
    'exposure':exposure,
    'fund_required': exposure + capital*1.5
    
    }
    update_performance_file(performance_data)

def evaluate_strategy(data, strategy):
    """
    Evaluate the strategy using data from the queue.

    Parameters:

    """
    collective_df = []
    tradebooks = []
    
    if data is None:  
        print("Received None, breaking the loop")  
        return
    
    if data:  
        df = pd.DataFrame(data)
        column_names = ["id", "timestamp", "symbol", "expiry", "type", "strike", "open", "high", "low", "close", "oi", "volume", "provider", "upload_time","implied_futures_weekly","implied_futures_monthly"]
        df.columns = column_names
        # print(df)
        df = df[df['symbol'] == f'{strategy.instrument}-I.NFO']
        implied_futures = df[['timestamp','implied_futures_weekly', 'implied_futures_monthly']]
        implied_futures['timestamp'] = pd.to_datetime(implied_futures['timestamp'])
        df = df[['timestamp', 'symbol', 'open' , 'high' , 'low', 'close']]
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values(by='timestamp', inplace=True)
        df.reset_index(inplace=True, drop=True)
        timeframe_value = f'{strategy.timeframe}min'
        df = resample_ohlc_df(df,timeframe_value)
        df = pd.merge(df, implied_futures, on='timestamp', how='left')
        # print(df)
        collective_df.append(df)
        # tradebook = moving_crossover_strategy(strategy, df, strategy.short_ma, strategy.long_ma)
        # tradebooks.append(tradebook)
    
    if tradebooks:
        collective_tradebook = pd.concat(tradebooks, ignore_index=True)
        collective_tradebook = collective_tradebook.sort_values('entry_time')
        collective_df= pd.concat(collective_df, ignore_index=True)
        collective_df =collective_df.set_index('timestamp').resample('D').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}).dropna()
        collective_df['date'] = collective_df.index.date
        collective_df = collective_df.sort_values(by='date')
        collective_df.to_csv('daily_ohlc.csv',index=False)
        cumulative_pnl = round((collective_tradebook['pnl'].cumsum()),2)
        collective_tradebook.to_csv(f'./strategy/moving_average/{strategy.strat_name}_{strategy.instrument}_{strategy.start_time.replace(":", "")}_{strategy.end_time.replace(":", "")}_{strategy.short_ma}_{strategy.long_ma}_{strategy.timeframe}_{strategy.stop_loss}tradebook.csv',index=False)
# "moving_average":{"default_value":"sma", "types" :["sma","ema"]},
