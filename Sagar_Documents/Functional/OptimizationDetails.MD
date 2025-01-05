# Optimization Details

## Table of Contents
- [API Endpoints](#api-endpoints)
  - [1. Generate Combinations](#1-Generate-Combinations)
    - [Endpoint](#endpoint)
    - [Request and Method](#request-and-method)
    - [Response](#response)
  - [2. Retry Optimization](#2-retry-optimization)
    - [Endpoint](#endpoint)
    - [Request and Method](#request-and-method)
    - [Response](#response)
  - [3. Run Optimization](#3-Run-Optimization) 
    - [Endpoint](#endpoint)
    - [Request and Method](#request-and-method)
    - [Response](#response)
    
- [Deployment](#deployment)

## API Endpoints

### 1. Generate Combinations
#### Endpoint
```
http://127.0.0.1:8000/generateKey
```
#### Request and Method
- Method: POST
- Request Body:
```json
{
    "optimization_key": "20241012143000_strategy",
    "optimization_parameter": {
        "entry_time": {
            "min": "09:15",
            "max": "10:30",
            "interval": 15
        },
        "exit_time": "15:30",
        "last_entry_time": false,
        "fromdate": "2021-04-01",
        "id": 38,
        "implied_futures_expiry": "current",
        "increase_in_profit": 50,
        "index": "nifty",
        "lock_profit": 50,
        "name": "nifty_atm_sell",
        "overall_sl": 300,
        "overall_target": 1000,
        "profit_reaches": 1000,
        "square_off": "partial",
        "strategy_type": "intraday",
        "todate": "2021-04-30",
        "trail_profit": 100,
        "trailing_options": false,
        "underlying": "futures",
        "legs": [
            {
                "atm_straddle_premium": 1,
                "closest_premium": 50,
                "expiry": "Current",
                "id": 230,
                "leg_no": 0,
                "lots": 1,
                "no_of_reentry": {
                    "min": 1,
                    "max": 3,
                    "interval": 1
                },
                "option_type": "call",
                "percent_of_atm_strike_sign": "+",
                "percent_of_atm_strike_value": "0.5",
                "position": "sell",
                "range_breakout": false,
                "roll_strike": 0,
                "roll_strike_increase_in_profit": 0,
                "roll_strike_lock_profit": 0,
                "roll_strike_lock_profit_sign": "percent",
                "roll_strike_profit_reaches": 0,
                "roll_strike_stop_loss": 0,
                "roll_strike_stop_loss_sign": "points",
                "roll_strike_strike_type": "ATM",
                "roll_strike_trail_profit": 0,
                "roll_strike_trail_profit_sign": "points",
                "roll_strike_trailing_options": false,
                "simple_momentum": 10,
                "simple_momentum_direction": "+",
                "simple_momentum_range_breakout": "none",
                "simple_momentum_sign": "points",
                "straddle_width_sign": "+",
                "straddle_width_value": "0.5",
                "strategy_id": 38,
                "strike_selection_criteria": "strike",
                "strike_selection_criteria_increase_in_profit": {
                    "min": 2,
                    "max": 4,
                    "interval": 1
                },
                "strike_selection_criteria_lock_profit": 2,
                "strike_selection_criteria_lock_profit_sign": "percent",
                "strike_selection_criteria_profit_reaches": 4,
                "strike_selection_criteria_stop_loss": 25,
                "strike_selection_criteria_stop_loss_sign": "percent",
                "strike_selection_criteria_trail_profit": 2,
                "strike_selection_criteria_trail_profit_sign": "percent",
                "strike_selection_criteria_trailing_options": "lockntrail",
                "strike_type": "ATM"
            },
            {
                "atm_straddle_premium": 1,
                "closest_premium": 50,
                "expiry": "Current",
                "id": 231,
                "leg_no": 0,
                "lots": 1,
                "no_of_reentry": 1,
                "option_type": "put",
                "percent_of_atm_strike_sign": "+",
                "percent_of_atm_strike_value": "0.5",
                "position": "sell",
                "range_breakout": false,
                "roll_strike": 0,
                "roll_strike_increase_in_profit": 0,
                "roll_strike_lock_profit": 0,
                "roll_strike_lock_profit_sign": "points",
                "roll_strike_profit_reaches": 0,
                "roll_strike_stop_loss": 0,
                "roll_strike_stop_loss_sign": "points",
                "roll_strike_strike_type": "ATM",
                "roll_strike_trail_profit": 0,
                "roll_strike_trail_profit_sign": "points",
                "roll_strike_trailing_options": false,
                "simple_momentum": false,
                "simple_momentum_direction": "+",
                "simple_momentum_range_breakout": "none",
                "simple_momentum_sign": "points",
                "straddle_width_sign": "+",
                "straddle_width_value": "0.5",
                "strategy_id": 38,
                "strike_selection_criteria": "strike",
                "strike_selection_criteria_increase_in_profit": 4,
                "strike_selection_criteria_lock_profit": 2,
                "strike_selection_criteria_lock_profit_sign": "percent",
                "strike_selection_criteria_profit_reaches": 4,
                "strike_selection_criteria_stop_loss": 25,
                "strike_selection_criteria_stop_loss_sign": "percent",
                "strike_selection_criteria_trail_profit": 2,
                "strike_selection_criteria_trail_profit_sign": "percent",
                "strike_selection_criteria_trailing_options": "lock",
                "strike_type": "ATM"
            }
        ]
    },
    "strategy_parameter": {
        "entry_time": "09:30",
        "exit_time": "15:15",
        "fromdate": "2021-04-01",
        "id": 38,
        "implied_futures_expiry": "current",
        "increase_in_profit": 50,
        "index": "nifty",
        "last_entry_time": "15:15",
        "legs": [
            {
                "atm_straddle_premium": 1,
                "closest_premium": 50,
                "expiry": "Current",
                "id": 230,
                "leg_no": 0,
                "lots": 1,
                "no_of_reentry": 3,
                "option_type": "call",
                "percent_of_atm_strike_sign": "+",
                "percent_of_atm_strike_value": "0.5",
                "position": "sell",
                "range_breakout": "0",
                "roll_strike": 0,
                "roll_strike_increase_in_profit": 0,
                "roll_strike_lock_profit": 0,
                "roll_strike_lock_profit_sign": "percent",
                "roll_strike_profit_reaches": 0,
                "roll_strike_stop_loss": 0,
                "roll_strike_stop_loss_sign": "points",
                "roll_strike_strike_type": "ATM",
                "roll_strike_trail_profit": 0,
                "roll_strike_trail_profit_sign": "points",
                "roll_strike_trailing_options": "lock",
                "simple_momentum": 0,
                "simple_momentum_direction": "+",
                "simple_momentum_range_breakout": "none",
                "simple_momentum_sign": "points",
                "straddle_width_sign": "+",
                "straddle_width_value": "0.5",
                "strategy_id": 38,
                "strike_selection_criteria": "strike",
                "strike_selection_criteria_increase_in_profit": 4,
                "strike_selection_criteria_lock_profit": 2,
                "strike_selection_criteria_lock_profit_sign": "percent",
                "strike_selection_criteria_profit_reaches": 4,
                "strike_selection_criteria_stop_loss": 25,
                "strike_selection_criteria_stop_loss_sign": "percent",
                "strike_selection_criteria_trail_profit": 2,
                "strike_selection_criteria_trail_profit_sign": "percent",
                "strike_selection_criteria_trailing_options": "lockntrail",
                "strike_type": "ATM"
            },
            {
                "atm_straddle_premium": 1,
                "closest_premium": 50,
                "expiry": "Current",
                "id": 231,
                "leg_no": 0,
                "lots": 1,
                "no_of_reentry": 3,
                "option_type": "put",
                "percent_of_atm_strike_sign": "+",
                "percent_of_atm_strike_value": "0.5",
                "position": "sell",
                "range_breakout": "0",
                "roll_strike": 0,
                "roll_strike_increase_in_profit": 0,
                "roll_strike_lock_profit": 0,
                "roll_strike_lock_profit_sign": "points",
                "roll_strike_profit_reaches": 0,
                "roll_strike_stop_loss": 0,
                "roll_strike_stop_loss_sign": "points",
                "roll_strike_strike_type": "ATM",
                "roll_strike_trail_profit": 0,
                "roll_strike_trail_profit_sign": "points",
                "roll_strike_trailing_options": "lock",
                "simple_momentum": 0,
                "simple_momentum_direction": "+",
                "simple_momentum_range_breakout": "none",
                "simple_momentum_sign": "points",
                "straddle_width_sign": "+",
                "straddle_width_value": "0.5",
                "strategy_id": 38,
                "strike_selection_criteria": "strike",
                "strike_selection_criteria_increase_in_profit": 4,
                "strike_selection_criteria_lock_profit": 2,
                "strike_selection_criteria_lock_profit_sign": "percent",
                "strike_selection_criteria_profit_reaches": 4,
                "strike_selection_criteria_stop_loss": 25,
                "strike_selection_criteria_stop_loss_sign": "percent",
                "strike_selection_criteria_trail_profit": 2,
                "strike_selection_criteria_trail_profit_sign": "percent",
                "strike_selection_criteria_trailing_options": "lockntrail",
                "strike_type": "ATM"
            }
        ],
        "lock_profit": 50,
        "name": "nifty_atm_sell",
        "overall_sl": 300,
        "overall_target": 300,
        "profit_reaches": 300,
        "square_off": "partial",
        "strategy_type": "intraday",
        "todate": "2021-04-04",
        "trail_profit": 30,
        "trailing_options": "lockntrail",
        "underlying": "futures"
    }
}


```
#### Response
```json
{
  "total_number_of_combinations": 54
}

```

### 2. Retry Optimization

#### Endpoint
```
http://127.0.0.1:8000/retryOptimization
```

#### Request and Method
- Method: POST
- Request Body:
```json
{
  "optimization_key": "20241011143000_strategy"
}
```

#### Response
```json
{
  "completed_combinations": [
    {
      "netProfit": -2678.5,
      "parameters": {
        "id": 38,
        "legs": [
          {
            "id": 230,
            "lots": 1,
            "expiry": "Current",
            "leg_no": 0,
            "position": "sell",
            "option_type": "call",
            "roll_strike": 0,
            "strategy_id": 38,
            "strike_type": "ATM",
            "no_of_reentry": 1,
            "range_breakout": false,
            "closest_premium": 50,
            "simple_momentum": 10,
            "straddle_width_sign": "+",
            "atm_straddle_premium": 1,
            "simple_momentum_sign": "points",
            "straddle_width_value": "0.5",
            "roll_strike_stop_loss": 0,
            "roll_strike_lock_profit": 0,
            "roll_strike_strike_type": "ATM",
            "roll_strike_trail_profit": 0,
            "simple_momentum_direction": "+",
            "strike_selection_criteria": "strike",
            "percent_of_atm_strike_sign": "+",
            "roll_strike_profit_reaches": 0,
            "roll_strike_stop_loss_sign": "points",
            "percent_of_atm_strike_value": "0.5",
            "roll_strike_lock_profit_sign": "percent",
            "roll_strike_trailing_options": false,
            "roll_strike_trail_profit_sign": "points",
            "roll_strike_increase_in_profit": 0,
            "simple_momentum_range_breakout": "none",
            "strike_selection_criteria_stop_loss": 25,
            "strike_selection_criteria_lock_profit": 2,
            "strike_selection_criteria_trail_profit": 2,
            "strike_selection_criteria_profit_reaches": 4,
            "strike_selection_criteria_stop_loss_sign": "percent",
            "strike_selection_criteria_lock_profit_sign": "percent",
            "strike_selection_criteria_trailing_options": "lockntrail",
            "strike_selection_criteria_trail_profit_sign": "percent",
            "strike_selection_criteria_increase_in_profit": 2
          },
          {
            "id": 231,
            "lots": 1,
            "expiry": "Current",
            "leg_no": 0,
            "position": "sell",
            "option_type": "put",
            "roll_strike": 0,
            "strategy_id": 38,
            "strike_type": "ATM",
            "no_of_reentry": 1,
            "range_breakout": false,
            "closest_premium": 50,
            "simple_momentum": false,
            "straddle_width_sign": "+",
            "atm_straddle_premium": 1,
            "simple_momentum_sign": "points",
            "straddle_width_value": "0.5",
            "roll_strike_stop_loss": 0,
            "roll_strike_lock_profit": 0,
            "roll_strike_strike_type": "ATM",
            "roll_strike_trail_profit": 0,
            "simple_momentum_direction": "+",
            "strike_selection_criteria": "strike",
            "percent_of_atm_strike_sign": "+",
            "roll_strike_profit_reaches": 0,
            "roll_strike_stop_loss_sign": "points",
            "percent_of_atm_strike_value": "0.5",
            "roll_strike_lock_profit_sign": "points",
            "roll_strike_trailing_options": false,
            "roll_strike_trail_profit_sign": "points",
            "roll_strike_increase_in_profit": 0,
            "simple_momentum_range_breakout": "none",
            "strike_selection_criteria_stop_loss": 25,
            "strike_selection_criteria_lock_profit": 2,
            "strike_selection_criteria_trail_profit": 0,
            "strike_selection_criteria_profit_reaches": 4,
            "strike_selection_criteria_stop_loss_sign": "percent",
            "strike_selection_criteria_lock_profit_sign": "percent",
            "strike_selection_criteria_trailing_options": "lock",
            "strike_selection_criteria_trail_profit_sign": "percent",
            "strike_selection_criteria_increase_in_profit": 0
          }
        ],
        "name": "nifty_atm_sell",
        "index": "nifty",
        "todate": "2021-04-30",
        "fromdate": "2021-04-01",
        "exit_time": "15:30",
        "entry_time": "09:15",
        "overall_sl": 300,
        "square_off": "partial",
        "underlying": "futures",
        "lock_profit": 0,
        "trail_profit": 0,
        "strategy_type": "intraday",
        "overall_target": 1000,
        "profit_reaches": 0,
        "last_entry_time": false,
        "trailing_options": false,
        "optimization_flag": true,
        "increase_in_profit": 0,
        "implied_futures_expiry": "current"
      },
      "averageLoss": -721.04,
      "expenctancy": -0.2,
      "maxDrawDown": 3660.06,
      "losingStrike": 5,
      "losingTrades": 13,
      "averageProfit": 1115.83,
      "winningStrike": 2,
      "winningTrades": 6,
      "numberOfTrades": 38,
      "systemDrawdown": "0",
      "totalBrokerage": {},
      "maxDrawDownDuration": 3
    },
    {
      "netProfit": 5627.5,
      "parameters": {
        "id": 38,
        "legs": [
          {
            "id": 230,
            "lots": 1,
            "expiry": "Current",
            "leg_no": 0,
            "position": "sell",
            "option_type": "call",
            "roll_strike": 0,
            "strategy_id": 38,
            "strike_type": "ATM",
            "no_of_reentry": 2,
            "range_breakout": false,
            "closest_premium": 50,
            "simple_momentum": 10,
            "straddle_width_sign": "+",
            "atm_straddle_premium": 1,
            "simple_momentum_sign": "points",
            "straddle_width_value": "0.5",
            "roll_strike_stop_loss": 0,
            "roll_strike_lock_profit": 0,
            "roll_strike_strike_type": "ATM",
            "roll_strike_trail_profit": 0,
            "simple_momentum_direction": "+",
            "strike_selection_criteria": "strike",
            "percent_of_atm_strike_sign": "+",
            "roll_strike_profit_reaches": 0,
            "roll_strike_stop_loss_sign": "points",
            "percent_of_atm_strike_value": "0.5",
            "roll_strike_lock_profit_sign": "percent",
            "roll_strike_trailing_options": false,
            "roll_strike_trail_profit_sign": "points",
            "roll_strike_increase_in_profit": 0,
            "simple_momentum_range_breakout": "none",
            "strike_selection_criteria_stop_loss": 25,
            "strike_selection_criteria_lock_profit": 2,
            "strike_selection_criteria_trail_profit": 2,
            "strike_selection_criteria_profit_reaches": 4,
            "strike_selection_criteria_stop_loss_sign": "percent",
            "strike_selection_criteria_lock_profit_sign": "percent",
            "strike_selection_criteria_trailing_options": "lockntrail",
            "strike_selection_criteria_trail_profit_sign": "percent",
            "strike_selection_criteria_increase_in_profit": 2
          },
          {
            "id": 231,
            "lots": 1,
            "expiry": "Current",
            "leg_no": 0,
            "position": "sell",
            "option_type": "put",
            "roll_strike": 0,
            "strategy_id": 38,
            "strike_type": "ATM",
            "no_of_reentry": 1,
            "range_breakout": false,
            "closest_premium": 50,
            "simple_momentum": false,
            "straddle_width_sign": "+",
            "atm_straddle_premium": 1,
            "simple_momentum_sign": "points",
            "straddle_width_value": "0.5",
            "roll_strike_stop_loss": 0,
            "roll_strike_lock_profit": 0,
            "roll_strike_strike_type": "ATM",
            "roll_strike_trail_profit": 0,
            "simple_momentum_direction": "+",
            "strike_selection_criteria": "strike",
            "percent_of_atm_strike_sign": "+",
            "roll_strike_profit_reaches": 0,
            "roll_strike_stop_loss_sign": "points",
            "percent_of_atm_strike_value": "0.5",
            "roll_strike_lock_profit_sign": "points",
            "roll_strike_trailing_options": false,
            "roll_strike_trail_profit_sign": "points",
            "roll_strike_increase_in_profit": 0,
            "simple_momentum_range_breakout": "none",
            "strike_selection_criteria_stop_loss": 25,
            "strike_selection_criteria_lock_profit": 2,
            "strike_selection_criteria_trail_profit": 0,
            "strike_selection_criteria_profit_reaches": 4,
            "strike_selection_criteria_stop_loss_sign": "percent",
            "strike_selection_criteria_lock_profit_sign": "percent",
            "strike_selection_criteria_trailing_options": "lock",
            "strike_selection_criteria_trail_profit_sign": "percent",
            "strike_selection_criteria_increase_in_profit": 0
          }
        ],
        "name": "nifty_atm_sell",
        "index": "nifty",
        "todate": "2021-04-30",
        "fromdate": "2021-04-01",
        "exit_time": "15:30",
        "entry_time": "09:30",
        "overall_sl": 300,
        "square_off": "partial",
        "underlying": "futures",
        "lock_profit": 0,
        "trail_profit": 0,
        "strategy_type": "intraday",
        "overall_target": 1000,
        "profit_reaches": 0,
        "last_entry_time": false,
        "trailing_options": false,
        "optimization_flag": true,
        "increase_in_profit": 0,
        "implied_futures_expiry": "current"
      },
      "averageLoss": -351.81,
      "expenctancy": 0.84,
      "maxDrawDown": 1550.46,
      "losingStrike": 4,
      "losingTrades": 9,
      "averageProfit": 879.38,
      "winningStrike": 4,
      "winningTrades": 10,
      "numberOfTrades": 42,
      "systemDrawdown": "0",
      "totalBrokerage": {},
      "maxDrawDownDuration": 7
    }
  ],
  "pending_combinations": {
    "pending_count": 52,
    "sequence_start": 2
  },
  "full_json": {
    "optimization_key": "20241011143000_strategy",
    "strategy_parameter": {
      "id": 38,
      "legs": [
        {
          "id": 230,
          "lots": 1,
          "expiry": "Current",
          "leg_no": 0,
          "position": "sell",
          "option_type": "call",
          "roll_strike": 0,
          "strategy_id": 38,
          "strike_type": "ATM",
          "no_of_reentry": 3,
          "range_breakout": "0",
          "closest_premium": 50,
          "simple_momentum": 0,
          "straddle_width_sign": "+",
          "atm_straddle_premium": 1,
          "simple_momentum_sign": "points",
          "straddle_width_value": "0.5",
          "roll_strike_stop_loss": 0,
          "roll_strike_lock_profit": 0,
          "roll_strike_strike_type": "ATM",
          "roll_strike_trail_profit": 0,
          "simple_momentum_direction": "+",
          "strike_selection_criteria": "strike",
          "percent_of_atm_strike_sign": "+",
          "roll_strike_profit_reaches": 0,
          "roll_strike_stop_loss_sign": "points",
          "percent_of_atm_strike_value": "0.5",
          "roll_strike_lock_profit_sign": "percent",
          "roll_strike_trailing_options": "lock",
          "roll_strike_trail_profit_sign": "points",
          "roll_strike_increase_in_profit": 0,
          "simple_momentum_range_breakout": "none",
          "strike_selection_criteria_stop_loss": 25,
          "strike_selection_criteria_lock_profit": 2,
          "strike_selection_criteria_trail_profit": 2,
          "strike_selection_criteria_profit_reaches": 4,
          "strike_selection_criteria_stop_loss_sign": "percent",
          "strike_selection_criteria_lock_profit_sign": "percent",
          "strike_selection_criteria_trailing_options": "lockntrail",
          "strike_selection_criteria_trail_profit_sign": "percent",
          "strike_selection_criteria_increase_in_profit": 4
        },
        {
          "id": 231,
          "lots": 1,
          "expiry": "Current",
          "leg_no": 0,
          "position": "sell",
          "option_type": "put",
          "roll_strike": 0,
          "strategy_id": 38,
          "strike_type": "ATM",
          "no_of_reentry": 3,
          "range_breakout": "0",
          "closest_premium": 50,
          "simple_momentum": 0,
          "straddle_width_sign": "+",
          "atm_straddle_premium": 1,
          "simple_momentum_sign": "points",
          "straddle_width_value": "0.5",
          "roll_strike_stop_loss": 0,
          "roll_strike_lock_profit": 0,
          "roll_strike_strike_type": "ATM",
          "roll_strike_trail_profit": 0,
          "simple_momentum_direction": "+",
          "strike_selection_criteria": "strike",
          "percent_of_atm_strike_sign": "+",
          "roll_strike_profit_reaches": 0,
          "roll_strike_stop_loss_sign": "points",
          "percent_of_atm_strike_value": "0.5",
          "roll_strike_lock_profit_sign": "points",
          "roll_strike_trailing_options": "lock",
          "roll_strike_trail_profit_sign": "points",
          "roll_strike_increase_in_profit": 0,
          "simple_momentum_range_breakout": "none",
          "strike_selection_criteria_stop_loss": 25,
          "strike_selection_criteria_lock_profit": 2,
          "strike_selection_criteria_trail_profit": 2,
          "strike_selection_criteria_profit_reaches": 4,
          "strike_selection_criteria_stop_loss_sign": "percent",
          "strike_selection_criteria_lock_profit_sign": "percent",
          "strike_selection_criteria_trailing_options": "lockntrail",
          "strike_selection_criteria_trail_profit_sign": "percent",
          "strike_selection_criteria_increase_in_profit": 4
        }
      ],
      "name": "nifty_atm_sell",
      "index": "nifty",
      "todate": "2021-04-04",
      "fromdate": "2021-04-01",
      "exit_time": "15:15",
      "entry_time": "09:30",
      "overall_sl": 300,
      "square_off": "partial",
      "underlying": "futures",
      "lock_profit": 50,
      "trail_profit": 30,
      "strategy_type": "intraday",
      "overall_target": 300,
      "profit_reaches": 300,
      "last_entry_time": "15:15",
      "trailing_options": "lockntrail",
      "increase_in_profit": 50,
      "implied_futures_expiry": "current"
    },
    "optimization_parameter": {
      "id": 38,
      "legs": [
        {
          "id": 230,
          "lots": 1,
          "expiry": "Current",
          "leg_no": 0,
          "position": "sell",
          "option_type": "call",
          "roll_strike": 0,
          "strategy_id": 38,
          "strike_type": "ATM",
          "no_of_reentry": {
            "max": 3,
            "min": 1,
            "interval": 1
          },
          "range_breakout": false,
          "closest_premium": 50,
          "simple_momentum": 10,
          "straddle_width_sign": "+",
          "atm_straddle_premium": 1,
          "simple_momentum_sign": "points",
          "straddle_width_value": "0.5",
          "roll_strike_stop_loss": 0,
          "roll_strike_lock_profit": 0,
          "roll_strike_strike_type": "ATM",
          "roll_strike_trail_profit": 0,
          "simple_momentum_direction": "+",
          "strike_selection_criteria": "strike",
          "percent_of_atm_strike_sign": "+",
          "roll_strike_profit_reaches": 0,
          "roll_strike_stop_loss_sign": "points",
          "percent_of_atm_strike_value": "0.5",
          "roll_strike_lock_profit_sign": "percent",
          "roll_strike_trailing_options": false,
          "roll_strike_trail_profit_sign": "points",
          "roll_strike_increase_in_profit": 0,
          "simple_momentum_range_breakout": "none",
          "strike_selection_criteria_stop_loss": 25,
          "strike_selection_criteria_lock_profit": 2,
          "strike_selection_criteria_trail_profit": 2,
          "strike_selection_criteria_profit_reaches": 4,
          "strike_selection_criteria_stop_loss_sign": "percent",
          "strike_selection_criteria_lock_profit_sign": "percent",
          "strike_selection_criteria_trailing_options": "lockntrail",
          "strike_selection_criteria_trail_profit_sign": "percent",
          "strike_selection_criteria_increase_in_profit": {
            "max": 4,
            "min": 2,
            "interval": 1
          }
        },
        {
          "id": 231,
          "lots": 1,
          "expiry": "Current",
          "leg_no": 0,
          "position": "sell",
          "option_type": "put",
          "roll_strike": 0,
          "strategy_id": 38,
          "strike_type": "ATM",
          "no_of_reentry": 1,
          "range_breakout": false,
          "closest_premium": 50,
          "simple_momentum": false,
          "straddle_width_sign": "+",
          "atm_straddle_premium": 1,
          "simple_momentum_sign": "points",
          "straddle_width_value": "0.5",
          "roll_strike_stop_loss": 0,
          "roll_strike_lock_profit": 0,
          "roll_strike_strike_type": "ATM",
          "roll_strike_trail_profit": 0,
          "simple_momentum_direction": "+",
          "strike_selection_criteria": "strike",
          "percent_of_atm_strike_sign": "+",
          "roll_strike_profit_reaches": 0,
          "roll_strike_stop_loss_sign": "points",
          "percent_of_atm_strike_value": "0.5",
          "roll_strike_lock_profit_sign": "points",
          "roll_strike_trailing_options": false,
          "roll_strike_trail_profit_sign": "points",
          "roll_strike_increase_in_profit": 0,
          "simple_momentum_range_breakout": "none",
          "strike_selection_criteria_stop_loss": 25,
          "strike_selection_criteria_lock_profit": 2,
          "strike_selection_criteria_trail_profit": 2,
          "strike_selection_criteria_profit_reaches": 4,
          "strike_selection_criteria_stop_loss_sign": "percent",
          "strike_selection_criteria_lock_profit_sign": "percent",
          "strike_selection_criteria_trailing_options": "lock",
          "strike_selection_criteria_trail_profit_sign": "percent",
          "strike_selection_criteria_increase_in_profit": 4
        }
      ],
      "name": "nifty_atm_sell",
      "index": "nifty",
      "todate": "2021-04-30",
      "fromdate": "2021-04-01",
      "exit_time": "15:30",
      "entry_time": {
        "max": "10:30",
        "min": "09:15",
        "interval": 15
      },
      "overall_sl": 300,
      "square_off": "partial",
      "underlying": "futures",
      "lock_profit": 50,
      "trail_profit": 100,
      "strategy_type": "intraday",
      "overall_target": 1000,
      "profit_reaches": 1000,
      "last_entry_time": false,
      "trailing_options": false,
      "increase_in_profit": 50,
      "implied_futures_expiry": "current"
    }
  }
}
```

### 3. Run Optimization

#### Endpoint
```
http://127.0.0.1:8000/runOptimization
```

#### Request and Method
- Method: POST
- Request Body:
```json
{
  "optimization_key":"20241011143000_strategy",
  "sequence_id" : 2
}

```

#### Response
```json
```
## Deployment
This guide will help you deploy the Strategy Optimization API on a server.
In this folder, locate the `db_credentials` section and update the credentials in your script according to your MySQL database configuration.

### 1. Set UP MYSQL database crendetials:

# Strategy Optimization Setup and Deployment

This guide will help you set up the necessary environment and deploy the strategy optimization script.

## 1. Set Up MySQL Database Credentials

1. Navigate to the following folder in your project:

    ```
    Sagar_Backend\time_based_strategy\strategy_optimization
    ```

2. Locate the section in the script where the database credentials are defined and update the credentials according to your MySQL database settings.

    In the script, you will find the following block of code:

    ```python
    db_credentials = {
        'host': 'localhost',
        'user': 'root',
        'password': 'pegasus',
        'database': 'sagar_strategy'
    }
    ```

3. Update the values for `'host'`, `'user'`, `'password'`, and `'database'` to match your MySQL setup. For example:

    ```python
    db_credentials = {
        'host': 'your_host',
        'user': 'your_user',
        'password': 'your_password',
        'database': 'your_database'
    }
    ```

## 2. Install Required Packages

Before running the script, ensure that all the required packages are installed. This can be done by using the `requirements.txt` file.


1. Open your terminal or command prompt.
2. Navigate to the project directory where the `requirements.txt` file is located.
3. Run the following command:

    ```bash
    pip install -r requirements.txt
    ```

This command will install all the necessary Python packages for the project.
```bash
pip install -r requirements.txt

