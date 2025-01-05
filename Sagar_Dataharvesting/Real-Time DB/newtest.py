import json

# Example buffer list (replace with your actual data)
buffer = [
    '\\"{\\"MessageCode\\":1512,\\"MessageVersion\\":4,\\"ApplicationType\\":0,\\"TokenID\\":0,\\"ExchangeSegment\\":1,\\"ExchangeInstrumentID\\":26000,\\"BookType\\":1,\\"XMarketType\\":1,\\"LastTradedPrice\\":23564.9,\\"LastTradedQunatity\\":0,\\"LastUpdateTime\\":1403191349,\\"PercentChange\\":0.42,\\"Close\\":23465.6}\\"',
    '\\"{\\"MessageCode\\":1512,\\"MessageVersion\\":4,\\"ApplicationType\\":0,\\"TokenID\\":0,\\"ExchangeSegment\\":1,\\"ExchangeInstrumentID\\":26000,\\"BookType\\":1,\\"XMarketType\\":1,\\"LastTradedPrice\\":23564.9,\\"LastTradedQunatity\\":0,\\"LastUpdateTime\\":1403191349,\\"PercentChange\\":0.42,\\"Close\\":23465.6}\\"',
    '\\"{\\"MessageCode\\":1512,\\"MessageVersion\\":4,\\"ApplicationType\\":0,\\"TokenID\\":0,\\"ExchangeSegment\\":1,\\"ExchangeInstrumentID\\":26000,\\"BookType\\":1,\\"XMarketType\\":1,\\"LastTradedPrice\\":23564.75,\\"LastTradedQunatity\\":0,\\"LastUpdateTime\\":1403191350,\\"PercentChange\\":0.42,\\"Close\\":23465.6}\\"',
    '\\"{\\"MessageCode\\":1512,\\"MessageVersion\\":4,\\"ApplicationType\\":0,\\"TokenID\\":0,\\"ExchangeSegment\\":1,\\"ExchangeInstrumentID\\":26000,\\"BookType\\":1,\\"XMarketType\\":1,\\"LastTradedPrice\\":23564.75,\\"LastTradedQunatity\\":0,\\"LastUpdateTime\\":1403191350,\\"PercentChange\\":0.42,\\"Close\\":23465.6}\\"',
    '\\"{\\"MessageCode\\":1512,\\"MessageVersion\\":4,\\"ApplicationType\\":0,\\"TokenID\\":0,\\"ExchangeSegment\\":1,\\"ExchangeInstrumentID\\":26000,\\"BookType\\":1,\\"XMarketType\\":1,\\"LastTradedPrice\\":23565.3,\\"LastTradedQunatity\\":0,\\"LastUpdateTime\\":1403191350,\\"PercentChange\\":0.42,\\"Close\\":23465.6}\\"'
]

# Accessing and processing each JSON object
for item in buffer:
    # Replace double backslashes with single backslashes
    clean_item = item.replace('\\"', '"')
    
    # Remove surrounding double quotes and decode the JSON string
    json_data = json.loads(clean_item.strip('"'))

    # Accessing individual fields
    print(json_data)
    print(f"Last Traded Price: {json_data['LastTradedPrice']}")
    print(f"Last Update Time: {json_data['LastUpdateTime']}")
    print()  # Empty line for separation
