# 15	Entry 930 Exit 15.15, Sell ATM Straddle Based on Implied Future, Condition Simple Momentum (-10%) SL on Individual Leg 25% Trail SL,4%-2%-1%, Reentry-3, @ Cost on SL , Strategy SL 300 Target 1000,Trail SL,300-50-30															
# 	Add hedge otm 5 condotion orb 10.45 SL 50 points trail SL 50-20-10, rentry @ cost 3			

import requests

url = "http://localhost:8000/run_strategies/"
print("Sending request")
# Entry 930 Exit 15.15, Sell ATM Straddle Based on Implied Future,
# Condition Simple Momentum (-10%) SL on Individual Leg 25% Trail SL,4%-2%-1%,
# Reentry-3, @ Cost on SL , Strategy SL 300 Target 1000,Trail SL,300-50-30
payload = [
    {
        "strategy_details": {
            "name": "UseCasePayload_03",
            "index": "NIFTY 50",
            "underlying": "implied_futures",
            "strategy_type": "intraday",
            "start_date": "2021-04-04",
            "end_date": "2021-05-05",
            "entry_time": "09:30:00",
            "last_entry_time": "15:15:00",
            "exit_time": "15:15:00",
            "square_off": "partial",
            "overall_sl": 300,
            "overall_target": 1000,
            "trailing_for_strategy": {'trail_value_type':'profit', 'trail_type':'lock', 'priceMove':300, 'sl_adjustment':50},
            "implied_futures_expiry": "monthly"
        },
        "legs": [
            {
                "leg_name": "ce_leg",
                "total_lots": 1,
                "position": "sell",
                "option_type": "CE",
                "expiry": "current",
                "strike_selection_criteria": {
                    "strike_selection": "strike",
                    "value": "ATM"
                },
                "roll_strike": False,
                "new_strike_selection_criteria": False,
                "stop_loss": ["points", 40],
                "trailing_sl": {'trail_value_type':'points', 'trail_type':'lock', 'priceMove':50, 'sl_adjustment':20},
                "no_of_reentry": 3,
                "simple_momentum": {"value_type":"percentage", "direction":"increment", "value":10},
                "range_breakout": False
            },
            {
                "leg_name": "ce_hedge_leg",
                "total_lots": 1,
                "position": "buy",
                "option_type": "CE",
                "expiry": "current",
                "strike_selection_criteria": {
                    "strike_selection": "strike",
                    "value": "OTM5"
                },
                "roll_strike": False,
                "new_strike_selection_criteria": False,
                "stop_loss": ["points", 300],
                "trailing_sl":False,
                "no_of_reentry": 0,
                "simple_momentum": False,
                "range_breakout": False
            },
            {
                "leg_name": "pe_leg",
                "total_lots": 1,
                "position": "sell",
                "option_type": "PE",
                "expiry": "current",
                "strike_selection_criteria": {
                    "strike_selection": "strike",
                    "value": "ATM"
                },
                "roll_strike": False,
                "new_strike_selection_criteria": False,
                "stop_loss": ["points", 40],
                "trailing_sl": {'trail_value_type':'points', 'trail_type':'lock', 'priceMove':50, 'sl_adjustment':20},
                "no_of_reentry": 3,
                "simple_momentum": {"value_type":"percentage", "direction":"increment", "value":10},
                "range_breakout": False
            },   
            {
                "leg_name": "pe_hedge_leg",
                "total_lots": 1,
                "position": "buy",
                "option_type": "CE",
                "expiry": "current",
                "strike_selection_criteria": {
                    "strike_selection": "strike",
                    "value": "OTM5"
                },
                "roll_strike": False,
                "new_strike_selection_criteria": False,
                "stop_loss": ["points", 300],
                "trailing_sl":False,
                "no_of_reentry": 0,
                "simple_momentum": False,
                "range_breakout": False
            },  
        ]
    }
]

response = requests.post(url, json=payload)

print(response.json())												