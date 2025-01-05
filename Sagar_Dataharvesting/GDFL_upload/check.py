import pandas as pd
from constants import *

def check_expiry_data():
    expiry_data = pd.read_csv(f'{INSTRUMENT_NAME}_expiry_data.csv')
    
    date_columns = ['trading_day', 'current_expiry', 'monthly_expiry']
    for col in date_columns:
        expiry_data[col] = pd.to_datetime(expiry_data[col])
    
    expiry_data['days_to_current_expiry'] = (expiry_data['current_expiry'] - expiry_data['trading_day']).dt.days
    
    expiry_data['last_day_of_month'] = expiry_data['trading_day'] + pd.offsets.MonthEnd(0)
    
    expiry_data['days_from_month_end_to_monthly_expiry'] = (expiry_data['monthly_expiry'] - expiry_data['last_day_of_month']).dt.days
    
    print(expiry_data[['trading_day', 'current_expiry', 'monthly_expiry', 'days_to_current_expiry', 'last_day_of_month', 'days_from_month_end_to_monthly_expiry']])
    expiry_data.to_csv(f'{INSTRUMENT_NAME}_expiry_data_with_days.csv', index=False)
check_expiry_data()
