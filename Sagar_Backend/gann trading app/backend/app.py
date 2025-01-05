import streamlit as st
from datetime import datetime
from broker.zerodha import zerodha_login
from helpers.utils import load_config, get_last_trading_day_data, convert_to_datetime
import pandas as pd
import os
from strategy.gann_level.gann import gann_calculator

config_file_path = os.path.join(os.path.dirname(__file__), 'strategy', 'gann_level','config.ini')
config = load_config(config_file_path)
user_parameters = config['SYSTEM']
symbol = user_parameters['SYMBOL']
creds = config['CREDS']
gann_metrics = config['GANN_METRICS']
reference_day = convert_to_datetime(gann_metrics['ANCHOR_DATE'])
reference_angle = gann_metrics['ANGLE_INTERVAL']

def main():
    st.title('Zerodha Dashboard')

    config_file_path = os.path.join(os.path.dirname(__file__), 'strategy', 'gann_level','config.ini')
    config = load_config(config_file_path)
    user_parameters = config['SYSTEM']
    # symbol = f'NSE:{user_parameters['SYMBOL']}'
    creds = config['CREDS']
    kite = zerodha_login(creds)
    print(kite.profile())
    # prev_day_quote = kite.quote(symbol)
    # prev_day_close = prev_day_quote[symbol]['last_price']
    prev_day_close, previous_trading_day = get_last_trading_day_data(kite,symbol)
    sun, square_of_nine, square_of_nine_multiplier, square_root_of_prev_day_close, price_at_sun, price_at_sunpoint = gann_calculator(previous_trading_day,reference_day,prev_day_close)
    holdings = pd.DataFrame(kite.holdings())

    st.header('Holdings')
    st.write(holdings)
    st.write('reference date :', reference_day)
    st.write('last trading date :', previous_trading_day)
    st.header('Calculated Values')
    st.write('prev_day_close:', prev_day_close)
    st.write('Sun:', sun)
    st.write('Square of Nine:', square_of_nine)
    st.write('Square of Nine Multiplier:', square_of_nine_multiplier)
    st.write('Square Root of Previous Day Close:', square_root_of_prev_day_close)
    st.write('Price at Sun:', price_at_sun)
    st.write('Price at Sun point:', price_at_sunpoint)

if __name__ == "__main__":
    main()
