class Strategy:
    def __init__(self):
        pass

    def pass_to_function(self, parameters):
        for param, values in parameters.items():
            print("Parameter:", param)
            print("Default Value:", values.get('default_value'))
            print("Min Value:", values.get('min_value'))
            print("Max Value:", values.get('max_value'))
            print("Increment:", values.get('increment', 'N/A'))

parameters = {
    "START_TIME": {'default_value': "9:30", 'min_value': '9:30', 'max_value': '14:20', 'increment': '15 minutes'},
    "END_TIME": {'default_value': "15:15", 'min_value': '12:30', 'max_value': '15:15', 'increment': '15 minutes'},
    "LAST_SIGNAL_ENTRY_TIME": {'default_value': "2:30"},
    "CANDLE_TIMEFRAME": {'default_value': "3M", 'possible_values': ['3M', '5M', '15M']},
    "SIGNAL_HALT_TIME": {'default_value': "NO TRADE TIME"},
    "LONG PERIOD": {'default_value': 100, 'min_value': 7, 'max_value': 300, 'increment': 1},
    "SHORT PERIOD": {'default_value': 50, 'min_value': 3, 'max_value': 295, 'increment': 1},
    "MinimumGap": {'default_value': 3, 'min_value': 3, 'max_value': 100, 'increment': 1},
    "MaximumGap": {'default_value': 10, 'min_value': 10, 'max_value': 100, 'increment': 1},
    "ma_type" : None # "EMA/SMA/WMA/DEMA/TEMA/KAMA": 

    }

strategy = Strategy()
strategy.pass_to_function(parameters)
