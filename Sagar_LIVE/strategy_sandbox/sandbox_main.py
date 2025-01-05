import asyncio
from datetime import datetime
from Strategy import Strategy
from LegBuilder import LegBuilder
from sandboxMarketSocket import MDSocket_io
from sandboxInteractiveSocket import OrderSocket_io
from datetime import datetime
from sandboxBroker import XTS
from creds import creds
from utils import get_atm, create_tradebook_table, broker_login
from Publisher import Publisher
import time
publisher = Publisher()
create_tradebook_table()
import warnings
import asyncio
warnings.filterwarnings("ignore")
port = "localhost:5001" 
interactive_port = '8050'
xts = XTS()  

# market_token, interactive_token, userid = broker_login(xts, creds)
# xts.market_token, xts.interactive_token, xts.userid  = market_token, interactive_token, userid
# xts.update_master_db()
soc = MDSocket_io( port=port, publisher=publisher) #initialize 
interactive_soc = OrderSocket_io(interactive_port, publisher)
# soc.on_connect = on_connect
# el = soc.get_emitter()
# el.on('connect', soc.on_connect)
# el.on('1512-json-full', soc.on_message1512_json_full)
soc.connect()



interactive_soc.connect()
# interactive_soc.on_trade = on_trade
interactive_el = interactive_soc.get_emitter()
interactive_el.on('trade', interactive_soc.on_trade)
interactive_el.on('order', interactive_soc.on_order)

# xts.get_master({'exchangeSegmentList': ['NSEFO']})

async def process_leg(leg):
    leg.get_expiry_df()
    leg.selection_criteria()
    await leg.leg_place_order()
    await leg.calculate_mtm()
  
async def run_strategy(xts, strategy_details):
    strategy = Strategy(xts, **strategy_details)
    time_now = datetime.now()
    print(f"time is {datetime.now()}")
    print(time_now, strategy.entry_time)
    if time_now < strategy.entry_time:
        print(f'sleeping for {(strategy.entry_time - time_now).total_seconds()}')
        await asyncio.sleep((strategy.entry_time - time_now).total_seconds())

    underlying_ltp = 53600#strategy.get_underlying_ltp()
    print(f"underlying ltp is {underlying_ltp}")
    if not underlying_ltp:
        retry_counter = 0
        while retry_counter <=3:
            print(f"retrying underlying_ltp retrieval for {retry_counter + 1} times")
            underlying_ltp = strategy.get_underlying_ltp()
            if underlying_ltp :
                return underlying_ltp
            retry_counter += 1
            await asyncio.sleep(2)
        underlying_ltp = None
        
    if underlying_ltp:
        print(f'{strategy.index} selected {strategy.underlying} and the last traded price is {underlying_ltp}')
        base = 100 if strategy.index == 'NIFTY BANK' else 50
        underlying_atm = get_atm(underlying_ltp, base)

        leg1 = LegBuilder(xts, soc, interactive_soc, f"{strategy.name}leg1", strategy, publisher, 2, 'buy', 'CE', 'current',
                        {'strike_selection': 'strike', 'value': 'OTM3'}, strike=underlying_atm, roll_strike=False,
                        new_strike_selection_criteria=3, stop_loss=['points', 20], trailing_sl=False, no_of_reentry=2, 
                        simple_momentum=False, range_breakout=False)
        leg2 = LegBuilder(xts, soc, interactive_soc, f"{strategy.name}leg2", strategy, publisher, 2, 'buy', 'PE', 'current',
                        {'strike_selection': 'strike', 'value': 'OTM3'}, underlying_atm, roll_strike=False,
                        new_strike_selection_criteria=3, stop_loss=['points', 20], trailing_sl=False, no_of_reentry=2, 
                        simple_momentum=False, range_breakout=False)
        # leg2 = LegBuilder(xts, soc, interactive_soc, f"{strategy.name}leg2", strategy, publisher, 2, 'sell', 'PE', 'current',
        #                 {'strike_selection': 'closest_premium', 'value': 400}, underlying_atm, roll_strike=False,
        #                 new_strike_selection_criteria=3, stop_loss=['points', 15], trailing_sl={"priceMove": 20, "sl_adjustment": 4}, no_of_reentry=2, 
        #                 simple_momentum=False, range_breakout=False)
        
        legs = [leg1, leg2]
        # legs = [leg1]

        await asyncio.gather(
            process_leg(leg1),
            process_leg(leg2),
            strategy.calculate_overall_pnl(legs)
        )
    else:
        print('unable to find underlying ltp, exiting !!')
        return
        

async def main():

    strategy_details_1 = {
        'name': 'strategy1', 'index': 'NIFTY BANK', 'underlying': 'spot', 'strategy_type': 'intraday',
        'entry_time': "11:01", 'last_entry_time': "23:59", 'exit_time': "23:59", 'square_off': "partial",
        'overall_sl': 1000, 'overall_target': 3000,                   
        'trailing_for_strategy': {"type": "lock_and_trail", "profit": 800, "lock_value": 500, "trail_level":  200, "trail_value": 100}, 
        'implied_futures_expiry': 'current', 'socket':soc
    }
   
    await asyncio.gather(
        run_strategy(xts, strategy_details_1),
        # run_strategy(xts, strategy_details_2)
    )

asyncio.run(main())
