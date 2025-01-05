from helpers import fetch_and_process_options_data
import pandas as pd
path = r"E:\New folder\new\Sagar_Dataharvesting\Real-Time DB\data_harvesting 2.0\fo\op221124.csv"
import re
import json
df= pd.read_csv(path)
df = df[df["TRD_NO_CON"]>= 2000]
df = df[df['CONTRACT_D'].str.split('-').str[1]=='NOV']
instruments = pd.read_csv("nfo.csv", low_memory=False)
instruments = instruments[instruments['Series']=='OPTSTK']





def parse_symbol(symbol):
    # Remove the prefix 'OPTSTK' or 'OPTIDX'
    if symbol.startswith('OPTSTK'):
        sym = symbol[len('OPTSTK'):]
    elif symbol.startswith('OPTIDX'):
        sym = symbol[len('OPTIDX'):]
    else:
        sym = symbol

    # Regular expression to parse the symbol
    pattern = r'^([A-Z]+)(\d{1,2}-[A-Z]{3}-\d{4})(CE|PE)(\d+(\.\d+)?)$'
    match = re.match(pattern, sym)
    if match:
        name = match.group(1)
        date_str = match.group(2)
        option_type = match.group(3)
        strike = match.group(4)

        # Extract month and last 2 digits of the year
        day, month, year = date_str.split('-')
        last2year = year[-2:]

        # Format the new symbol
        new_symbol = f"{name}{last2year}{month}{strike}{option_type}"
        return new_symbol
    else:
        # Return the original symbol if it doesn't match the pattern
        return symbol

# Apply the function to the CONTRACT_D column
df['symbol'] = df['CONTRACT_D'].apply(parse_symbol)

symbol_lists = df['symbol'].tolist()

final_df = instruments[instruments['Description'].isin(symbol_lists)]
df_subset = final_df.head(400)

# Step 2: Create the list of dictionaries
list_of_dicts = df_subset['ExchangeInstrumentID'].apply(
    lambda x: {'exchangeInstrumentID': int(x), 'exchangeSegment': 2}
).tolist()

# Step 3: Save the list to a JSON file
with open('deepak.json', 'w') as f:
    json.dump(list_of_dicts, f, indent=4)