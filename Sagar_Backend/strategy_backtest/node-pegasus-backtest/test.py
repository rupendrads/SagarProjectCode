import json
from datetime import datetime, timedelta
from itertools import product
import time
from timeit import timeit
import json
import requests
import os
from optimizer.optimizer import Optimizer 
symbol_name = 'nifty'
params_json = '''
    {
    "start_time": {"default_value": "09:30", "min_time": "09:30", "max_time": "12:00", "difference": 5},
        "end_time": {"default_value": "14:30", "min_time": "14:30", "max_time": "15:00", "difference": 15},
        "short_ma": {"period_name": "ShortPeriod", "default_value": 15, "min_value": 5, "max_value": 30, "increment": 2},
        "long_ma": {"period_name": "LongPeriod", "default_value": 30, "min_value": 10, "max_value": 50, "increment": 2},
        "timeframe": {"period_name": "timeframe", "default_value": 1, "min_value": 1, "max_value": 30, "increment": 1},
        "rule": {"parameter_list": ["short_ma", "long_ma"], "relation": "5 <= long_ma - short_ma && long_ma - short_ma < 20"},
        "moving_average":{"default_value":"ema", "types" :["sma","ema"]}
    
    }
    '''
today_date = datetime.today().strftime('%Y-%m-%d')

optimizer = Optimizer(params_json,calculate_combinations=True)
combinations = optimizer.generate_final_combination_list()
combinations = [dict(t) for t in {tuple(sorted(d.items())) for d in combinations}]
url = 'http://localhost:3000/applyRule'
chunk_size = 50000

chunks = [combinations[i:i + chunk_size] for i in range(0, len(combinations), chunk_size)]
results_list ={}
instrument_name  = 'nifty'
json_file_path = f"{symbol_name}_{today_date}.json"
with open(json_file_path, "w") as json_file:
    json_file.write('[')

    for chunk in chunks:
        payload = {'combinations': chunk}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            results = response.json()["results"]
            for result in results:
                combo = result["combination"]
                json.dump(combo, json_file)
                json_file.write(',')
        else:
            print('Error:', response.json()['error'])
with open(json_file_path, "r+") as json_file:
    json_file.seek(0, os.SEEK_END)
    json_file.seek(json_file.tell() - 1, os.SEEK_SET)
    json_file.truncate()
    json_file.write(']')


print(f'finished calculation')

