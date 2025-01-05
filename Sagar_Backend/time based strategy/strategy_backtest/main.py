import asyncio
from datetime import datetime
from Strategy import Strategy
from LegBuilder import LegBuilder
from utils import read_strategy_folder, process_pnl_files
import time
import warnings
import asyncio
warnings.filterwarnings("ignore")

async def run_strategy(strategy_details):
    strategy = Strategy(**strategy_details)
    # leg1 = LegBuilder(f"{strategy.name}leg1", strategy, 2, 25, 'sell', 'CE', 'current',
    #                 {'strike_selection': 'atm_pct',  'value':{'atm_strike':'+','input': 0.005}}, roll_strike=False,
    #                 new_strike_selection_criteria=3, stop_loss=['points', 20], trailing_sl=False, no_of_reentry=0, 
    #                 simple_momentum=False, range_breakout=False)
    # leg1 = LegBuilder(f"{strategy.name}leg1", strategy, 1, 25, 'sell', 'CE', 'current',
    #                 {'strike_selection': 'strike',  'value':'ATM'}, roll_strike=False,
    #                 new_strike_selection_criteria={"profit":300, "strike":100, "roll_sl": 20}, stop_loss=['points', 30], trailing_sl=False, no_of_reentry=0, 
    #                 simple_momentum={"value_type":"points","value":20, "direction":"increment"}, range_breakout=False)
    leg1 = LegBuilder(f"{strategy.name}leg1", strategy, 1, 25, 'sell', 'CE', 'current',
                    {'strike_selection': 'strike',  'value':'ATM'}, roll_strike=False,
                    new_strike_selection_criteria=False, stop_loss=['points', 30], trailing_sl=False, no_of_reentry=0, 
                    simple_momentum={'value_type':'points', 'value':20, 'direction': 'increment' }, range_breakout=False)
    # leg2 = LegBuilder(f"{strategy.name}leg2", strategy, 1, 25, 'sell', 'PE', 'current',
    #                 {'strike_selection': 'strike',  'value':'ATM'}, roll_strike=False,
    #                 new_strike_selection_criteria=False, stop_loss=['points', 30], trailing_sl=False, no_of_reentry=0, 
    #                 simple_momentum=False, range_breakout=False)
    # leg2 = LegBuilder(f"{strategy.name}leg2", strategy, 1, 25, 'sell', 'PE', 'current',
    #                 {'strike_selection': 'strike',  'value':'ATM'}, roll_strike=False,
    #                 new_strike_selection_criteria=False, stop_loss=['points', 30], trailing_sl=False, no_of_reentry=0, 
    #                 simple_momentum=False, range_breakout=False)
    # leg3 = LegBuilder(f"{strategy.name}leg3", strategy, 1, 25, 'buy', 'CE', 'current',
    #                 {'strike_selection': 'strike',  'value':'OTM4'}, roll_strike=False,
    #                 new_strike_selection_criteria=False, stop_loss=['points', 30], trailing_sl=False, no_of_reentry=0, 
    #                 simple_momentum=False, range_breakout=False)
    # leg4 = LegBuilder(f"{strategy.name}leg1", strategy, 1, 25, 'buy', 'CE', 'current',
    #                 {'strike_selection': 'strike',  'value':'OTM4'}, roll_strike=False,
    #                 new_strike_selection_criteria=False, stop_loss=['points', 30], trailing_sl=False, no_of_reentry=0, 
    #                 simple_momentum=False, range_breakout=False)
    # {"value_type":"points","value":20, "direction":"increment"}

    # leg2 = LegBuilder(f"{strategy.name}leg2", strategy, 1, 25, 'sell', 'PE', 'current',
    #                 {'strike_selection': 'strike',  'value':'OTM3'}, roll_strike=False,
    #                 new_strike_selection_criteria=3, stop_loss=['points', 30], trailing_sl=False, no_of_reentry=0, 
    #                 simple_momentum=False, range_breakout=False)
    # leg3 = LegBuilder(f"{strategy.name}leg3", strategy, 1, 25, 'sell', 'CE', 'current',
    #                 {'strike_selection': 'closest_premium', 'value': 80}, roll_strike=False,
    #                 new_strike_selection_criteria=3, stop_loss=['points', 20], trailing_sl={"trail_type":"lock", "priceMove": 20, "sl_adjustment": 4}, no_of_reentry=0, 
    #                 simple_momentum=False, range_breakout=False)
    # leg1 = LegBuilder(f"{strategy.name}leg1", strategy, 1, 25, 'sell', 'CE', 'current',
    #                 {'strike_selection': 'closest_premium', 'value': 80}, roll_strike=False,
    #                 new_strike_selection_criteria=3, stop_loss=['points', 15], trailing_sl={"trail_type":"lock_and_trail", "lock_adjustment":{"priceMove": 15, "sl_adjustment": 5}, "trail_adjustment":{"priceMove": 10, "sl_adjustment": 5}}, no_of_reentry=3, 
    #                 simple_momentum=False, range_breakout=False) 
    # leg2 = LegBuilder(f"{strategy.name}leg2", strategy, 1, 25, 'sell', 'PE', 'current',
    #                 {'strike_selection': 'closest_premium', 'value': 80}, roll_strike=False,
    #                 new_strike_selection_criteria=3, stop_loss=['points', 20], trailing_sl={"trail_type":"lock", "priceMove": 15, "sl_adjustment": 5}, no_of_reentry=0, 
    #                 simple_momentum=False, range_breakout=False) 
    # leg1 = LegBuilder(f"{strategy.name}leg1", strategy, 2, 75, 'sell', 'PE', 'current',
    #                 {'strike_selection': 'strike', 'value': 'OTM3'}, roll_strike=False,
    #                 new_strike_selection_criteria=3, stop_loss=['points', 50], trailing_sl={"priceMove": 20, "sl_adjustment": 4}, no_of_reentry=0, 
    #                 simple_momentum=False, range_breakout={"timeframe":3, "breach_side":"high"})
    # leg2 = LegBuilder(f"{strategy.name}leg2", strategy, 2, 75, 'sell', 'PE', 'current',
    #                 {'strike_selection': 'closest_premium', 'value': 200}, roll_strike=False,
    #                 new_strike_selection_criteria=3, stop_loss=['points', 15], trailing_sl={"priceMove": 20, "sl_adjustment": 4}, no_of_reentry=2, 
    #                 simple_momentum=False, range_breakout=False)
    leg1.backtest_selection()
    # leg2.backtest_selection()
    # leg3.backtest_selection()
    read_strategy_folder(strategy.name)
    # # print(strategy.overall_target, strategy.overall_sl)
    process_pnl_files(strategy.name)
    # process_pnl_files(strategy.name, strategy.overall_target, strategy.overall_sl)

    # strategy.combined_legs(legs)
    # leg2.backtest_selection()
    # print(leg1.minutewise_tradebook)
    # print(min(leg1.minutewise_tradebook['pnl']))
    # print(max(leg1.minutewise_tradebook['pnl']))
    # leg2.backtest_selection()
    # leg2 = LegBuilder(f"{strategy.name}leg2", strategy, 2, 'sell', 'PE', 'current',
    #                 {'strike_selection': 'closest_premium', 'value': 200}, roll_strike=False,
    #                 new_strike_selection_criteria=3, stop_loss=['points', 15], trailing_sl={"priceMove": 20, "sl_adjustment": 4}, no_of_reentry=2, 
    #                 simple_momentum=False, range_breakout=False)


#     #     leg1 = LegBuilder(xts, 'soc', interactive_soc, f"{strategy.name}leg1", strategy, publisher, 2, 'sell', 'CE', 'current',
#     #                     {'strike_selection': 'closest_premium', 'value': 200}, underlying_atm, roll_strike=False,
#     #                     new_strike_selection_criteria=3, stop_loss=['points', 15], trailing_sl={"priceMove": 20, "sl_adjustment": 4}, no_of_reentry=2, 
#     #                     simple_momentum=False, range_breakout=False)
#     #     leg2 = LegBuilder(xts, 'soc', interactive_soc, f"{strategy.name}leg2", strategy, publisher, 2, 'sell', 'PE', 'current',
#     #                     {'strike_selection': 'closest_premium', 'value': 200}, underlying_atm, roll_strike=False,
#     #                     new_strike_selection_criteria=3, stop_loss=['points', 15], trailing_sl={"priceMove": 20, "sl_adjustment": 4}, no_of_reentry=2, 
#     #                     simple_momentum=False, range_breakout=False)
#     #     # leg1 = LegBuilder(xts, 'soc', interactive_soc, f"{strategy.name}leg1", strategy, publisher, 2, 'sell', 'CE', 'current',
#     #     #                 {'strike_selection': 'closest_premium', 'value': 150}, underlying_atm, roll_strike=False,
#     #     #                 new_strike_selection_criteria=3, stop_loss=['points', 10], trailing_sl={"priceMove": 10, "sl_adjustment": 4}, no_of_reentry=2, 
#     #     #                 simple_momentum={'value_type':'points', 'value':15, 'direction': 'increment' }, range_breakout=False)
#     #     # leg2 = LegBuilder(xts, 'soc', interactive_soc, f"{strategy.name}leg2", strategy, publisher, 2, 'sell', 'PE', 'current',
#     #     #                 {'strike_selection': 'closest_premium', 'value': 150}, underlying_atm, roll_strike=False,
#     #     #                 new_strike_selection_criteria=3, stop_loss=['points', 10], trailing_sl={"priceMove": 10, "sl_adjustment": 4}, no_of_reentry=2, 
#     #     #                 simple_momentum={'value_type':'points', 'value':15, 'direction': 'increment' }, range_breakout=False)
#     #     # # leg3 = LegBuilder(xts, 'soc', 'interactive_soc', f"{strategy.name}leg3", strategy, publisher, 2, 'sell', 'PE', 'current',
#     #     # #                   {'strike_selection': 'strike', 'value': "ATM"}, underlying_atm, roll_strike=2,
#     #     # #                   new_strike_selection_criteria=3, stop_loss=['points', 50], trailing_sl={"priceMove": 4, "sl_adjustment": 4}, no_of_reentry=2, 
#     #     # #                   simple_momentum=False, range_breakout=False)
#     #     legs = [leg1, leg2]
#         # legs = [leg1]

#         await asyncio.gather(
#             process_leg(leg1),
#             process_leg(leg2),
#             strategy.calculate_overall_pnl(legs)
#         )
#     else:
#         print('unable to find underlying ltp, exiting !!')
#         return
        

async def main():

    strategy_details_2 = {
        'name': 'sm_test', 'index': 'NIFTY 50', 'underlying': 'fut', 'strategy_type': 'intraday','start_date': '2021-04-04', 'end_date':'2021-06-05',
        'entry_time': "09:30:00", 'last_entry_time': "14:30:00", 'exit_time': "14:30:00", 'square_off': "full",
        'overall_sl': False, 'overall_target': False, 
        'trailing_for_strategy': False,
        'implied_futures_expiry': False,
        
    }
    

    # {"type": "lock_and_trail", "profit": 0, "lock_value": 0, "trail_level":400, "trail_value": 100}
    await asyncio.gather(
        run_strategy(strategy_details_2),
    #     # run_strategy(xts, strategy_details_2)
    )

asyncio.run(main())
