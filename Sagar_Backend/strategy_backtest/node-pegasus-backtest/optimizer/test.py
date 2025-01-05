import json
from datetime import datetime, timedelta
from itertools import product
import time
from timeit import timeit
import json
import requests
import os
class Optimizer:
    def __init__(self, params_json, calculate_combinations=True):
        self.params = json.loads(params_json)
        self.calculate_combinations = calculate_combinations

    def generate_final_combination_list(self):
        if not self.calculate_combinations:
            default_parameters = {}
            print("\nDefault Parameter Values:")
            for param_name, param_value in self.params.items():
                if not param_name.startswith("rule"):
                    default_value = param_value.get("default_value", "")
                    default_parameters[param_name] = default_value
            default_parameters_list = []
            default_parameters_list.append(default_parameters)
            return default_parameters_list
        else:
            return self.generate_parameter_combinations()

    def apply_rule(self, combination):
        rule = self.params.get("rule", None)
        if rule:
            parameter_list = rule.get("parameter_list", [])
            relation = rule.get("relation", "")

            if parameter_list and relation:
                param_values = {param: combination[param] for param in parameter_list}
                if eval(relation, param_values):
                    return True
        return False

    def generate_parameter_combinations(self):
        parameter_combinations = []
        print("\nAll Parameter Combinations:")
        all_parameters = {}
        for param_name, param in self.params.items():
            if param_name == "rule":
                continue
            if "types" in param:
                all_parameters[param_name] = param["types"]
            else:
                all_parameters[param_name] = self.generate_period_list(param) if not self.is_time_format(param) else self.generate_time_list(param)

        for combination in product(*all_parameters.values()):
            params_combination = {}
            for param_name, value in zip(all_parameters.keys(), combination):
                params_combination[param_name] = value
                parameter_combinations.append(params_combination)

            # Apply rule to the combination
            # if not self.params.get("rule") or self.apply_rule(params_combination):
            #     parameter_combinations.append(params_combination)
            #     # if len(parameter_combinations) > 50:
                #     break
        return parameter_combinations

    def is_time_format(self, params):
        for value in params.values():
            if isinstance(value, str):
                try:
                    datetime.strptime(value, "%H:%M")
                    return True
                except ValueError:
                    pass
        return False

    def generate_time_list(self, params):
        start_time = params.get("default_value", "00:00")
        min_time = params.get("min_time", start_time)
        max_time = params.get("max_time", "23:59")
        difference = params.get("difference", 15)

        start = datetime.strptime(start_time, "%H:%M")
        min_time = datetime.strptime(min_time, "%H:%M")
        max_time = datetime.strptime(max_time, "%H:%M")

        time_list = [start.strftime("%H:%M")]

        current_time = start
        while current_time < max_time:
            current_time += timedelta(minutes=difference)
            if current_time <= max_time:
                time_list.append(current_time.strftime("%H:%M"))

        return time_list

    def generate_period_list(self, params):
        period_name = params.get("period_name", "")
        default_value = params.get("default_value", 1)
        min_value = params.get("min_value", 1)
        max_value = params.get("max_value", 60)
        increment = params.get("increment", 1)

        period_list = [min_value]
        current_value = min_value

        while current_value < max_value:
            current_value += increment
            if current_value <= max_value:
                period_list.append(current_value)

        return period_list

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

optimizer = Optimizer(params_json,calculate_combinations=True)
tbc = datetime.now()
combinations = optimizer.generate_final_combination_list()
print(len(combinations))
counter = 0
for combination in combinations:
    counter+=1
    print(combination)
    if counter >10:
        break

url = 'http://localhost:3000/applyRule'
chunk_size = 50000

chunks = [combinations[i:i + chunk_size] for i in range(0, len(combinations), chunk_size)]
results_list ={}
instrument_name  = 'nifty'
json_file_path = f'{instrument_name}.json'
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

tac = datetime.now()
print(f'time to calculate {tac-tbc}')
# with open(json_file, 'w') as payload:
#             json.dump(results_list, payload)
