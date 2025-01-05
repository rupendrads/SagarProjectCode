import pandas as pd
def dailywise_data(df):
    df = df[(df['timestamp'].dt.time >= pd.Timestamp('9:15').time()) & (df['timestamp'].dt.time <= pd.Timestamp('15:30').time())]
    grouped_df = df.groupby(df['timestamp'].dt.date)
    return grouped_df