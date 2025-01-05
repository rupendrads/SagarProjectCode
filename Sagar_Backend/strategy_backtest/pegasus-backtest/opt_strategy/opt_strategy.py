import concurrent.futures
import matplotlib.pyplot as plt
import pandas as pd
def process_group(date, group, short_window, long_window):
    tradebook = []
    stop_loss = 20
    exit_time = pd.Timestamp(year=group['timestamp'].iloc[0].year,
                             month=group['timestamp'].iloc[0].month,
                             day=group['timestamp'].iloc[0].day,
                             hour=15,
                             minute=0)
    in_trade = False
    entry_time = None
    entry_price = None  # Initialize entry price
    pnl = 0
    trades_per_day = 0
    for index, row in group.iterrows():
        if row['timestamp'].time() >= pd.Timestamp('09:20').time():
            if not in_trade and row['short_ma'] > row['long_ma']:
                in_trade = True
                entry_time = row['timestamp']
                entry_price = row['close']  # Update entry price
                trades_per_day += 1
            elif in_trade and (row['timestamp'] == exit_time or row['short_ma'] < row['long_ma'] or row['close'] < entry_price - stop_loss):
                in_trade = False
                exit_time = row['timestamp']
                exit_price = row['close']  # Calculate exit price
                pnl = exit_price - entry_price
                tradebook.append({'entry_time': entry_time,
                                  'exit_time': exit_time,
                                  'entry_price': entry_price,  # Store entry price
                                  'exit_price': exit_price,    # Store exit price
                                  'pnl': pnl,
                                  'trades_per_day': trades_per_day})

    return tradebook
def moving_crossover_strategy(df, short_window=50, long_window=200):
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
