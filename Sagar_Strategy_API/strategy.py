# -*- coding: utf-8 -*-
"""
Created on Thu May 16 00:14:43 2024

@author: Admin
"""

class Strategy:
  def __init__(self, id=2, name="RCB",underlying="Spot",strategy_type="Intrday",implied_futures_expiry="Current",entry_time="09:30",
               last_entry_time="10:30",exit_time="18:30",square_off="Complete",overall_sl=1,overall_target=1,trailing_options="Lock",
               profit_reaches=2,lock_profit=100,increase_in_profit=200,trail_profit=100):
    self.id=id
    self.name=name
    self.underlying=underlying
    self.strategy_type=strategy_type
    self.implied_futures_expiry=implied_futures_expiry
    self.entry_time=entry_time
    self.last_entry_time=last_entry_time
    self.exit_time=exit_time
    self.square_off=square_off
    self.overall_sl=overall_sl
    self.overall_target=overall_target
    self.trailing_options=trailing_options
    self.profit_reaches=profit_reaches
    self.lock_profit=lock_profit
    self.increase_in_profit=increase_in_profit
    self.trail_profit=trail_profit


  def Strategy_default(self):
    return self.id,self.name,self.underlying,self.strategy_type,self.implied_futures_expiry,self.entry_time,self.last_entry_time,self.exit_time,self.square_off,self.overall_sl,self.overall_target,self.trailing_options,self.profit_reaches,self.lock_profit,self.increase_in_profit,self.trail_profit

class Leg:
    def __init__(self, strategy,id=1,leg_no=2,lots=4,position="Buy",option_type="Call",expiry="Next",no_of_reentry="3",strike_selection_criteria="ABC",closest_premium="200",strike_type="ATM",straddle_width_value="12",straddle_width_sign="+",percent_of_atm_strike_value=50,percent_of_atm_strike_sign="=",atm_straddle_premium="123",strike_selection_criteria_stop_loss="442",strike_selection_criteria_stop_loss_sign="-",strike_selection_criteria_trailing_options="ABC",strike_selection_criteria_profit_reaches="600",strike_selection_criteria_lock_profit="300",strike_selection_criteria_lock_profit_sign="%",strike_selection_criteria_increase_in_profit="250",strike_selection_criteria_trail_profit="150",strike_selection_criteria_trail_profit_sign="%",roll_strike="220",roll_strike_strike_type="ABC",roll_strike_stop_loss="175",roll_strike_stop_loss_sign="%",roll_strike_trailing_options="ABC",roll_strike_profit_reaches="123",roll_strike_lock_profit="433",roll_strike_lock_profit_sign="%",roll_strike_increase_in_profit="300",roll_strike_trail_profit="400",roll_strike_trail_profit_sign="%",simple_momentum_range_breakout="rb",simple_momentum="222",simple_momentum_sign="%",simple_momentum_direction="+",range_breakout="test"):
       self.strategy = strategy
       self.id = id
       self.leg_no = leg_no
       self.lots = lots
       self.position = position
       self.option_type = option_type
       self.expiry = expiry
       self.no_of_reentry = no_of_reentry
       self.strike_selection_criteria = strike_selection_criteria
       self.closest_premium = closest_premium
       self.strike_type = strike_type
       self.straddle_width_value = straddle_width_value
       self.straddle_width_sign = straddle_width_sign
       self.percent_of_atm_strike_value = percent_of_atm_strike_value
       self.percent_of_atm_strike_sign = percent_of_atm_strike_sign
       self.atm_straddle_premium = atm_straddle_premium
       self.strike_selection_criteria_stop_loss = strike_selection_criteria_stop_loss
       self.strike_selection_criteria_stop_loss_sign = strike_selection_criteria_stop_loss_sign
       self.strike_selection_criteria_trailing_options = strike_selection_criteria_trailing_options
       self.strike_selection_criteria_profit_reaches = strike_selection_criteria_profit_reaches
       self.strike_selection_criteria_lock_profit = strike_selection_criteria_lock_profit
       self.strike_selection_criteria_lock_profit_sign = strike_selection_criteria_lock_profit_sign
       self.strike_selection_criteria_increase_in_profit = strike_selection_criteria_increase_in_profit
       self.strike_selection_criteria_trail_profit = strike_selection_criteria_trail_profit
       self.strike_selection_criteria_trail_profit_sign = strike_selection_criteria_trail_profit_sign
       self.roll_strike = roll_strike
       self.roll_strike_strike_type = roll_strike_strike_type
       self.roll_strike_stop_loss = roll_strike_stop_loss
       self.roll_strike_stop_loss_sign = roll_strike_stop_loss_sign
       self.roll_strike_trailing_options = roll_strike_trailing_options
       self.roll_strike_profit_reaches = roll_strike_profit_reaches
       self.roll_strike_lock_profit = roll_strike_lock_profit
       self.roll_strike_lock_profit_sign = roll_strike_lock_profit_sign
       self.roll_strike_increase_in_profit = roll_strike_increase_in_profit
       self.roll_strike_trail_profit = roll_strike_trail_profit
       self.roll_strike_trail_profit_sign = roll_strike_trail_profit_sign
       self.simple_momentum_range_breakout = simple_momentum_range_breakout
       self.simple_momentum = simple_momentum
       self.simple_momentum_sign = simple_momentum_sign
       self.simple_momentum_direction = simple_momentum_direction
       self.range_breakout = range_breakout

       

    def Leg_default(self):
       return self.id,self.strategy.id,self.leg_no,self.lots,self.position,self.option_type,self.expiry,self.no_of_reentry,self.strike_selection_criteria,self.closest_premium,self.strike_type,self.straddle_width_value,self.straddle_width_sign,self.percent_of_atm_strike_value,self.percent_of_atm_strike_sign,self.atm_straddle_premium,self.strike_selection_criteria_stop_loss,self.strike_selection_criteria_stop_loss_sign,self.strike_selection_criteria_trailing_options,self.strike_selection_criteria_profit_reaches,self.strike_selection_criteria_lock_profit,self.strike_selection_criteria_lock_profit_sign,self.strike_selection_criteria_increase_in_profit,self.strike_selection_criteria_trail_profit,self.strike_selection_criteria_trail_profit_sign,self.roll_strike,self.roll_strike_strike_type,self.roll_strike_stop_loss,self.roll_strike_stop_loss_sign,self.roll_strike_trailing_options,self.roll_strike_profit_reaches,self.roll_strike_lock_profit,self.roll_strike_lock_profit_sign,self.roll_strike_increase_in_profit,self.roll_strike_trail_profit,self.roll_strike_trail_profit_sign,self.simple_momentum_range_breakout,self.simple_momentum,self.simple_momentum_sign,self.simple_momentum_direction,self.range_breakout