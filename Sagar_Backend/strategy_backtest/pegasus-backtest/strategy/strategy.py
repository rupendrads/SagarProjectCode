# import os
class Strategy:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def display_parameters(self):
        print("Strategy parameters:")
        for key, value in self.__dict__.items():
            print(f"{key}: {value}")
    # def display_parameters(self):
    #     print("Strategy parameters:")
    #     for key, value in self.parameters.items():
    #         print(f"{key}: {value}")
# class Strategy:
#     def __init__(self, strat_name, start_date, end_date, instrument, is_intraday,
#                  start_time, end_time, capital, lots, stoploss_mtm_points=None,
#                  target=None, per_trade_commission=0,
#                  re_entry_count=0, re_execute_count=0, stoploss_mtm_rupees=None,
#                  timeframe="1min", opt_timeframe="1min", move_sl_to_cost=False,
#                  expiry_week=0, stoploss_pct=None,
#                  close_half_on_mtm_rupees=None,
#                  tsl=None):
#         self.strat_name = strat_name
#         self.start_date = start_date
#         self.end_date = end_date
#         self.instrument = instrument
#         self.is_intraday = is_intraday
#         self.start_time = start_time
#         self.end_time = end_time
#         self.capital = capital
#         self.lots = lots
#         self.stoploss_mtm_points = stoploss_mtm_points
#         self.target = target
#         self.per_trade_commission = per_trade_commission
#         self.re_entry_count = re_entry_count
#         self.re_execute_count = re_execute_count
#         self.stoploss_mtm_rupees = stoploss_mtm_rupees
#         self.timeframe = timeframe
#         self.opt_timeframe = opt_timeframe
#         self.move_sl_to_cost = move_sl_to_cost
#         self.expiry_week = expiry_week
#         self.stoploss_pct = stoploss_pct
#         self.close_half_on_mtm_rupees = close_half_on_mtm_rupees
#         self.tsl = tsl

#     def create_strat_dir(self):
#         curr_dir = os.path.dirname(os.path.dirname(__file__))
#         strategy_dir = os.path.join(curr_dir, self.strat_name)
#         if not os.path.exists(strategy_dir):
#             os.mkdir(strategy_dir)
