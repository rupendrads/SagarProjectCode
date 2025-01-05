import logging
from datetime import timedelta
import pandas as pd

def configure_logger(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger()

def calculate_expiry_sets(ce_data, pe_data, timestamp):
    ce_expiry_set = set(ce_data['expiry'])
    pe_expiry_set = set(pe_data['expiry'])

    ce_filtered_expiry_set = {expiry for expiry in ce_expiry_set if expiry.month == timestamp.month}
    pe_filtered_expiry_set = {expiry for expiry in pe_expiry_set if expiry.month == timestamp.month}
    max_expiry_in_month_ce = max(ce_filtered_expiry_set) if ce_filtered_expiry_set else None
    max_expiry_in_month_pe = max(pe_filtered_expiry_set) if pe_expiry_set else None

    if (max_expiry_in_month_ce) and max_expiry_in_month_ce.date() < timestamp.date():
        next_month = (timestamp.replace(day=28) + timedelta(days=4)).replace(day=1)
        ce_filtered_expiry_set = {expiry for expiry in ce_expiry_set if expiry.month == next_month.month}
        max_expiry_in_next_month_ce = max(ce_filtered_expiry_set) if ce_filtered_expiry_set else None

    if (max_expiry_in_month_pe) and max_expiry_in_month_pe.date() < timestamp.date():
        next_month = (timestamp.replace(day=28) + timedelta(days=4)).replace(day=1)
        pe_filtered_expiry_set = {expiry for expiry in pe_expiry_set if expiry.month == next_month.month}
        max_expiry_in_next_month_pe = max(pe_filtered_expiry_set) if pe_filtered_expiry_set else None

    return max_expiry_in_month_ce, max_expiry_in_month_pe

def forward_fill_implied_futures(df, column_name):
    for idx, row in df.iterrows():
        if pd.isnull(row[column_name]):
            if idx > 0:
                prev_close = df.iloc[idx-1]['close']
                prev_implied = df.iloc[idx-1][column_name]
                current_implied = prev_implied - prev_close + row['close']
                df.loc[idx, column_name] = round(current_implied, 2)
    return df
