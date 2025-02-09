export const defaultLeg = {
  id: Math.random() + 1,
  lots: "1",
  position: "sell",
  option_type: "call",
  expiry: "Current",
  no_of_reentry: 1,
  strike_selection_criteria: "strike",
  closest_premium: 0,
  strike_type: "ATM",
  straddle_width_value: 0.5,
  straddle_width_sign: "+",
  percent_of_atm_strike_value: 0.5,
  percent_of_atm_strike_sign: "+",
  atm_straddle_premium: 1,
  strike_selection_criteria_stop_loss: 0,
  strike_selection_criteria_stop_loss_sign: "points",
  strike_selection_criteria_trailing_options: "lock",
  strike_selection_criteria_profit_reaches: 0,
  strike_selection_criteria_lock_profit: 0,
  strike_selection_criteria_lock_profit_sign: "points",
  strike_selection_criteria_increase_in_profit: 0,
  strike_selection_criteria_trail_profit: 0,
  strike_selection_criteria_trail_profit_sign: "points",
  roll_strike: 0,
  roll_strike_strike_type: "ATM",
  roll_strike_stop_loss: 0,
  roll_strike_stop_loss_sign: "points",
  roll_strike_trailing_options: "lock",
  roll_strike_profit_reaches: 0,
  roll_strike_lock_profit: 0,
  roll_strike_lock_profit_sign: "points",
  roll_strike_increase_in_profit: 0,
  roll_strike_trail_profit: 0,
  roll_strike_trail_profit_sign: "points",
  simple_momentum_range_breakout: "none",
  simple_momentum: 0,
  simple_momentum_sign: "points",
  simple_momentum_direction: "+",
  range_breakout: 0,
};
