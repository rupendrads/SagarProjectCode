# -*- coding: utf-8 -*-
"""
Created on Thu May 16 00:11:25 2024

@author: Admin
"""

from flask import Flask, jsonify
from strategy import Strategy,Leg
#import mysql.connector

#mydb = mysql.connector.connect(
#host="localhost",
#user="root",
#password="root",
#database="sagar_strategy"
#)
api = Flask(__name__)

@api.route('/strategy', methods=['GET'])
def get_strategy():
    #mycursor = mydb.cursor()
    strat = Strategy()
    id,name,underlying,strategy_type,implied_futures_expiry,entry_time,last_entry_time,exit_time,square_off,overall_sl,overall_target,trailing_options,profit_reaches,lock_profit,increase_in_profit,trail_profit = strat.Strategy_default()  
    
    #query = f"INSERT INTO strategy (id,name,underlying,strategy_type,implied_futures_expiry,entry_time,last_entry_time,exit_time,square_off,overall_sl,overall_target,trailing_options,profit_reaches,lock_profit,increase_in_profit,trail_profit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    #values = (id,name,underlying,strategy_type,implied_futures_expiry,entry_time,last_entry_time,exit_time,square_off,overall_sl,overall_target,trailing_options,profit_reaches,lock_profit,increase_in_profit,trail_profit)
    #mycursor.execute(query, values)
    #mydb.commit()
    
    return jsonify({
        "id": id,
        "name": name,
        "underlying": underlying,
        "strategy_type": strategy_type,
        "implied_futures_expiry": implied_futures_expiry,
        "entry_time": entry_time,
        "last_entry_time": last_entry_time,
        "exit_time": exit_time,
        "square_off": square_off,
        "overall_sl": overall_sl,
        "overall_target": overall_target,
        "trailing_options": trailing_options,
        "profit_reaches": profit_reaches,
        "lock_profit": lock_profit,
        "increase_in_profit": increase_in_profit,
        "trail_profit": trail_profit
    })

@api.route('/leg', methods=['GET'])
def get_leg():
    #mycursor = mydb.cursor()
    strat = Strategy()
    leg = Leg(strat)
    id,strategy_id,leg_no,lots,position,option_type,expiry,no_of_reentry,strike_selection_criteria,closest_premium,strike_type,straddle_width_value,straddle_width_sign,percent_of_atm_strike_value,percent_of_atm_strike_sign,atm_straddle_premium,strike_selection_criteria_stop_loss,strike_selection_criteria_stop_loss_sign,strike_selection_criteria_trailing_options,strike_selection_criteria_profit_reaches,strike_selection_criteria_lock_profit,strike_selection_criteria_lock_profit_sign,strike_selection_criteria_increase_in_profit,strike_selection_criteria_trail_profit,strike_selection_criteria_trail_profit_sign,roll_strike,roll_strike_strike_type,roll_strike_stop_loss,roll_strike_stop_loss_sign,roll_strike_trailing_options,roll_strike_profit_reaches,roll_strike_lock_profit,roll_strike_lock_profit_sign,roll_strike_increase_in_profit,roll_strike_trail_profit,roll_strike_trail_profit_sign,simple_momentum_range_breakout,simple_momentum,simple_momentum_sign,simple_momentum_direction,range_breakout = leg.Leg_default()
    
    #query = f"INSERT INTO leg (id,strategy_id,leg_no,lots,position,option_type,expiry,no_of_reentry,strike_selection_criteria,closest_premium,strike_type,straddle_width_value,straddle_width_sign,percent_of_atm_strike_value,percent_of_atm_strike_sign,atm_straddle_premium,strike_selection_criteria_stop_loss,strike_selection_criteria_stop_loss_sign,strike_selection_criteria_trailing_options,strike_selection_criteria_profit_reaches,strike_selection_criteria_lock_profit,strike_selection_criteria_lock_profit_sign,strike_selection_criteria_increase_in_profit,strike_selection_criteria_trail_profit,strike_selection_criteria_trail_profit_sign,roll_strike,roll_strike_strike_type,roll_strike_stop_loss,roll_strike_stop_loss_sign,roll_strike_trailing_options,roll_strike_profit_reaches,roll_strike_lock_profit,roll_strike_lock_profit_sign,roll_strike_increase_in_profit,roll_strike_trail_profit,roll_strike_trail_profit_sign,simple_momentum_range_breakout,simple_momentum,simple_momentum_sign,simple_momentum_direction,range_breakout) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    #values = (id,strategy_id,leg_no,lots,position,option_type,expiry,no_of_reentry,strike_selection_criteria,closest_premium,strike_type,straddle_width_value,straddle_width_sign,percent_of_atm_strike_value,percent_of_atm_strike_sign,atm_straddle_premium,strike_selection_criteria_stop_loss,strike_selection_criteria_stop_loss_sign,strike_selection_criteria_trailing_options,strike_selection_criteria_profit_reaches,strike_selection_criteria_lock_profit,strike_selection_criteria_lock_profit_sign,strike_selection_criteria_increase_in_profit,strike_selection_criteria_trail_profit,strike_selection_criteria_trail_profit_sign,roll_strike,roll_strike_strike_type,roll_strike_stop_loss,roll_strike_stop_loss_sign,roll_strike_trailing_options,roll_strike_profit_reaches,roll_strike_lock_profit,roll_strike_lock_profit_sign,roll_strike_increase_in_profit,roll_strike_trail_profit,roll_strike_trail_profit_sign,simple_momentum_range_breakout,simple_momentum,simple_momentum_sign,simple_momentum_direction,range_breakout)
    #mycursor.execute(query, values)
    #mydb.commit()
    
    return jsonify({
        "id":id,
        "strategy_id":strategy_id,
        "leg_no":leg_no,
        "lots":lots,
        "position":position,
        "option_type":option_type,
        "expiry":expiry,
        "no_of_reentry":no_of_reentry,
        "strike_selection_criteria":strike_selection_criteria,
        "closest_premium":closest_premium,
        "strike_type":strike_type,
        "straddle_width_value":straddle_width_value,
        "straddle_width_sign":straddle_width_sign,
        "percent_of_atm_strike_value":percent_of_atm_strike_value,
        "percent_of_atm_strike_sign":percent_of_atm_strike_sign,
        "atm_straddle_premium":atm_straddle_premium,
        "strike_selection_criteria_stop_loss":strike_selection_criteria_stop_loss,
        "strike_selection_criteria_stop_loss_sign":strike_selection_criteria_stop_loss_sign,
        "strike_selection_criteria_trailing_options":strike_selection_criteria_trailing_options,
        "strike_selection_criteria_profit_reaches":strike_selection_criteria_profit_reaches,
        "strike_selection_criteria_lock_profit":strike_selection_criteria_lock_profit,
        "strike_selection_criteria_lock_profit_sign":strike_selection_criteria_lock_profit_sign,
        "strike_selection_criteria_increase_in_profit":strike_selection_criteria_increase_in_profit,
        "strike_selection_criteria_trail_profit":strike_selection_criteria_trail_profit,
        "strike_selection_criteria_trail_profit_sign":strike_selection_criteria_trail_profit_sign,
        "roll_strike":roll_strike,
        "roll_strike_strike_type":roll_strike_strike_type,
        "roll_strike_stop_loss":roll_strike_stop_loss,
        "roll_strike_stop_loss_sign":roll_strike_stop_loss_sign,
        "roll_strike_trailing_options":roll_strike_trailing_options,
        "roll_strike_profit_reaches":roll_strike_profit_reaches,
        "roll_strike_lock_profit":roll_strike_lock_profit,
        "roll_strike_lock_profit_sign":roll_strike_lock_profit_sign,
        "roll_strike_increase_in_profit":roll_strike_increase_in_profit,
        "roll_strike_trail_profit":roll_strike_trail_profit,
        "roll_strike_trail_profit_sign":roll_strike_trail_profit_sign,
        "simple_momentum_range_breakout":simple_momentum_range_breakout,
        "simple_momentum":simple_momentum,
        "simple_momentum_sign":simple_momentum_sign,
        "simple_momentum_direction":simple_momentum_direction,
        "range_breakout":range_breakout

        })
    
if __name__ == '__main__':
    api.run(debug=True)