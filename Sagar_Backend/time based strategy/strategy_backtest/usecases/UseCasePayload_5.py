import requests

url = "http://localhost:8000/run_strategies/"
print("Sending request")

payload = [
    {
        "strategy_details": {
            "name": "UseCasePayload_05",
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
                "stop_loss": ["percentage", 40],
                "trailing_sl": {'trail_value_type':'points', 'trail_type':'lock', 'priceMove':50, 'sl_adjustment':20},
                "no_of_reentry": 3,
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
                "stop_loss": ["percentage", 40],
                "trailing_sl": {'trail_value_type':'points', 'trail_type':'lock', 'priceMove':50, 'sl_adjustment':20},
                "no_of_reentry": 3,
                "simple_momentum": False,
                "range_breakout": False
            },
            
            
            
            
        ]
    }
]

response = requests.post(url, json=payload)

print(response.json())

