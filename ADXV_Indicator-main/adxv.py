import pandas as pd
import numpy as np
import json
from collections import defaultdict
import copy
import warnings

# Suppress RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)

global_df = pd.DataFrame()

class MAXVALUE:
    
    def __init__(self,json_data):
        self.json_data = json_data
               
        
    def get_max_value(self,json_data):
        
        data_list = self.json_data
        data = json.loads(data_list)
        close_prices = [item['Close'] for item in data]

        close_array = np.array(close_prices)

        currentUp = np.maximum(close_array - np.roll(close_array, 1), 0)

        currentDown = np.maximum(np.roll(close_array, 1) - close_array, 0)
   
        return currentUp,currentDown
    
    def nz(self, value):
        if value is None:
            return 0
        return value 
    
    def get_up_down(self,currentUp,currentDown,BarCount,k):
        #print(BarCount)
        up = [0] * BarCount  
        down = [0] * BarCount  
    
        for i in range(1, BarCount):
            prev_up = self.nz(up[i-1])  # Handle null value
            prev_down = self.nz(down[i-1])  # Handle null value
            up[i] = (1 - k) * prev_up + (k * currentUp[i])
            down[i] = (1 - k) * prev_down + (k * currentDown[i])     
        return up, down
    
    def get_ups_downs(self,fractionUp,fractionDown,BarCount,k):
        ups = [0] * BarCount  
        downs = [0] * BarCount  
        for i in range(1, BarCount):
            ups[i] = (1 - k) * self.nz(ups[i-1]) + (k * fractionUp[i])
            downs[i] = (1 - k) * self.nz(downs[i-1]) + (k * fractionDown[i])
        return ups,downs
    
    def get_index(self,normFraction,fractionUp,fractionDown,BarCount,k):
        index = [0] * BarCount  
        ups = [0] * BarCount 
        downs = [0] * BarCount
        for i in range(1, BarCount):
            index[i] = (1 - k) * self.nz(index[i-1]) + (k * normFraction[i])
            ups[i] = (1 - k) * self.nz(ups[i-1]) + (k * fractionUp[i])
            downs[i] = (1 - k) * self.nz(downs[i-1]) + (k * fractionDown[i])
        return index,ups,downs

    def get_adxvma(self,vIndex,close,BarCount,k):
        adxvma = [0] * BarCount 
        for i in range(1, BarCount):
            adxvma[i] = (1 - k * vIndex[i]) * self.nz(adxvma[i-1]) + (k * vIndex[i] * close[i])
        return adxvma

    def get_allvalues(self,new_data):
       open_prices = []
       high_prices =[]
       close_prices =[]
       low_prices =[]
        # Iterate over data points
       for point in new_data:
            price = point['last_trade_price'] 
            time = point['time']
            result = str(price) + " " + time
            open_prices.append(result)
            high_prices.append(result)
            close_prices.append(result)
            low_prices.append(result)

        # Calculate high, close, and low prices for the current minute
        
       high_price = max(high_prices)
       close_price = close_prices[-1]
       low_price = min(low_prices)

        # Reset arrays for the next minute
       open_prices.clear()
       high_prices.clear()
       close_prices.clear()
       low_prices.clear()

       return high_price, close_price, low_price
   
    def calculate_ohlcv(self,data_json):
    
        ohlcv_data = {}
        #print(data)
        data = json.loads(data_json)
    
        for item in data:
            #print(item)
            #print(item['ExchangeInstrumentID'])
            instrument_id = item['ExchangeInstrumentID']
            traded_price = item['LastTradedPrice']
            last_update_time = item['LastUpdateTime']
        
            # If the instrument ID is not already in the dictionary, initialize it
            if instrument_id not in ohlcv_data:
                ohlcv_data[instrument_id] = {
                    'open': traded_price,
                    'high': (traded_price, last_update_time),  # Store both high price and its update time
                    'low': traded_price,
                    'close': traded_price
                }
            else:
                # Update high and low values
                current_high_price, current_high_time = ohlcv_data[instrument_id]['high']
                if traded_price > current_high_price:
                    ohlcv_data[instrument_id]['high'] = (traded_price, last_update_time)
                ohlcv_data[instrument_id]['low'] = min(ohlcv_data[instrument_id]['low'], traded_price)
        
                # Update close value (the last traded price in the minute)
                ohlcv_data[instrument_id]['close'] = traded_price
            
        ohlcv_list = []
        for instrument_id, values in ohlcv_data.items():
            ohlcv_list.append({
                'ExchangeInstrumentID': instrument_id,
                'High': values['high'][0],  # Extract high price from the tuple
                 # Extract high price update time from the tuple
                'Low': values['low'],
                'Close': values['close'],
                'Open': values['open'],
                'Date Time': last_update_time
            })
    
        return ohlcv_list
    
    def sortresult(self,data):

        #print("rupendra + ", data)
        sorted_data = sorted(data, key=lambda x: x['ExchangeInstrumentID'])
        #print("sorted_data + ",sorted_data)
        for item in sorted_data:
            item['LastUpdateTime'] = item['LastUpdateTime'].isoformat()

# Serialize the sorted data to JSON
        sort_data = json.dumps(sorted_data, indent=4)
        data = json.loads(sort_data)
        #print(data)
        #print("sort_data:", sort_data)
        distinct_values = set(item['ExchangeInstrumentID'] for item in data)
        all_values= []
# Print the distinct values
        #print("Distinct ExchangeInstrumentID values:", distinct_values)
        for value in distinct_values:
            #print(value)
            filtered_data = filter(lambda x: x['ExchangeInstrumentID'] == value, data)
            #print("filtered_data + ", filtered_data)
            sorted_filtered_data = sorted(filtered_data, key=lambda x: x['LastUpdateTime'])
            #print("sorted_filtereed_data + ",sorted_filtered_data)
            sorted_filtered_json = json.dumps(sorted_filtered_data, indent=4)
            #print(sorted_filtered_json)
            #print("Sorted and filtered JSON: ",sorted_filtered_json)
            ohlc_data = MAXVALUE.calculate_ohlcv(self,sorted_filtered_json)
            #print(ohlc_data)
            #MAXVALUE.get_ohlc(self,ohlc_data)
            all_values.append(ohlc_data)
            #print()
            #MAXVALUE.calculate_laxman(self,ohlc_data,1)
        if all_values:
            MAXVALUE.get_ohlc(self,all_values)
         
    def get_ohlc(self,all_values):
        
        #print("ALLVALUES ", all_values)
        print("------------------------------------------")
        
        global global_df
        flattened_values = [item for sublist in all_values for item in sublist]
    
        # Convert the flattened list of dictionaries into a DataFrame
        all_values_df = pd.DataFrame(flattened_values)
    
        # Concatenate the new DataFrame with the global DataFrame
        global_df = pd.concat([global_df, all_values_df], ignore_index=True)
    
        #print(global_df)
    
        distinct_values = global_df['ExchangeInstrumentID'].unique()
        #print(distinct_values)
        period=3
        for value in distinct_values:
            #if value == 5888:
                filtered_df = global_df[global_df['ExchangeInstrumentID'] == value]
                sorted_df = filtered_df.sort_values(by='ExchangeInstrumentID')
                MAXVALUE.calculate_laxman(self, sorted_df, period=3)
            
        '''
        df_sorted = global_df.sort_values(by=['ExchangeInstrumentID','Date Time'])

        # Convert sorted DataFrame to JSON
        json_data = df_sorted.to_json(orient='records')

       # Print or save JSON data as needed
        #print("Output data : ",json_data)
        
        parsed_data = json.loads(json_data)
        #print(parsed_data)
        distinct_values = sorted(set(item['ExchangeInstrumentID'] for item in parsed_data))
        #print(distinct_values)
        instrument_data = {}
        for entry in parsed_data:
            instrument_id = entry['ExchangeInstrumentID']
            if instrument_id not in instrument_data:
                instrument_data[instrument_id] = []
            instrument_data[instrument_id].append(entry)
        all_entries = []
        print(instrument_id)
        # Iterate through each ExchangeInstrumentID and print its corresponding data
        
        for instrument_id, instrument_values in instrument_data.items():
                #print(f"ExchangeInstrumentID: {instrument_id}")
            for entry in instrument_values:
                        
                        #print(entry)
                all_entries.append(entry)
                #print(all_entries)
            #if len(all_entries) > 1:
               # MAXVALUE.calculate_laxman(self, all_entries, period=3)
            #all_entries.clear()
                #print()
        '''
    def calculate_laxman(self,sorted_df,period):
        adxvma_period = period
        ohlcv_data = sorted_df.to_json(orient='records', date_format='iso')
        ohlcv_records = json.loads(ohlcv_data)

        # Count the number of records
        num_records = len(ohlcv_records)
        
        #print("-----------------------")
        k = 1/adxvma_period
        if(num_records > 1):
            #print("OHLCV LENGTH ", num_records)
            #print("Period ", period)
                #print("OHLCV : ",ohlcv_data)
            atr_cal = ATRValue(ohlcv_data,period,sorted_df)
                #print("ATR_CAL + ",atr_cal)
            atr_cal.average_true_range()
                #print(atr_values)
            
            #print("Average True Range (ATR) values:", atr_values)
                #print("Close : ",close)
                #print(BarCount)
            '''
            if (true_length > period):
                
                #GET CURRENT UP AND DOWN
                max_test = MAXVALUE(ohlcv_data)
                currentUp,currentDown = max_test.get_max_value(ohlcv_data)
                        #print("Current Up:", currentUp)
                        #print("Current Down:", currentDown)
                
                up,down = max_test.get_up_down(currentUp,currentDown,BarCount,k)
                        #print("Up:", up)
                        #print("Down:", down)
                up = np.array(up)
                down = np.array(down)
                
                isum = up + down
                        #print("isum : ", isum)
                        #fractionUp = up/isum if isum>0 else 0
                        #fractionUp = np.where(isum > 0, np.divide(up, isum, out=np.zeros_like(up), where=isum!=0, dtype=np.float64), 0)
                fractionUp = np.where(isum > 0, up / isum.astype(float), 0)
                        #fractionDown = np.where(isum > 0, np.divide(down, isum, out=np.zeros_like(down), where=isum!=0,dtype=np.float64), 0)
                fractionDown = np.where(isum > 0, down.astype(float) / isum.astype(float), 0)
                
                        #print("fractionUp:", fractionUp)
                        #print("fractionDown:", fractionDown)
                
                ups,downs = max_test.get_ups_downs(fractionUp,fractionDown,BarCount,k)
                        #print(ups)
                        #print(downs)
                
                ups = np.array(ups)
                downs = np.array(downs)
                
                normDiff = abs(ups - downs);
                normSum = ups + downs;
                
                
                normFraction = np.where(normSum > 0.0, normDiff / normSum.astype(float), 0)
                
                        #print(normFraction)
                
                index,ups_value,downs_value = max_test.get_index(normFraction,fractionUp,fractionDown,BarCount,k)
                
                        #print("INDEX : ", index)
                        #print("UPS : ", ups_value)
                        #print("DOWNS : ", downs_value)
                
                index_data = np.array(index)
                        #adxvma_period_data = 3
                
                hhp_cal = HHPValue(index_data, adxvma_period)
                llp_cal = LLVValue(index_data, adxvma_period)
                
                hhp_result = hhp_cal.get_hhp_value()
                        #print("HHP : ",hhp_result)
                
                llp_result = llp_cal.get_llv_data()
                        #print("LLP : ",llp_result)
                
                ihhv = np.maximum(index, hhp_result)
                illv = np.minimum(index, llp_result)
                
                        #print("IHHV : ", ihhv)
                        #print("ILLV : ", illv)
                
                
                vIndex = np.where((ihhv - illv) > 0.0, (index - illv) / (ihhv - illv).astype(float), 0)
                
                
                        #print(vIndex)
                
                adxvma = max_test.get_adxvma(vIndex,close,BarCount,k)
                    #print(ohlcv_data)
                        #print("ADXVMA : ", adxvma)
                
                sorted_df['adxvma'] = adxvma
                print(sorted_df)
                        #global_df.update(sorted_df)
                        
                global_df.reset_index(drop=True, inplace=True)
                        
                        # Initialize an array to store the boolean mask
                filtered_rows = np.zeros(len(global_df), dtype=bool)
                        
                        # Loop through each row in sorted_df and find matching rows in global_df
                for index, row in sorted_df.iterrows():
                    print("ExchangeInstrumentID Row ",row["ExchangeInstrumentID"])
                    print(row["Date Time"])
                            # Filter 'global_df' based on ExchangeInstrumentID and DateTime
                    filtered_rows |= (global_df['ExchangeInstrumentID'] == row['ExchangeInstrumentID']) & (global_df['Date Time'] == row['Date Time'])
                            #print(filtered_rows)
                            #global_df.loc[filtered_rows, 'true_ranges'] = sorted_df['true_ranges']
                    global_df.loc[filtered_rows, 'adxvma'] = sorted_df['adxvma']
                        #(filtered_rows)
                        # Update the 'adxvma' column in the filtered rows
                        #global_df.loc[filtered_rows, 'adxvma'] = sorted_df['adxvma']
                        
                        # Print the updated DataFrame
                        #print(global_df)
                        
                          # Specify the file path where you want to save the CSV file
                
                        # Export the DataFrame to a CSV file
                '''        
            csv_file_path = "global_df_export.csv"
            global_df.to_csv(csv_file_path, index=False)
                            
            print(f"DataFrame has been exported to '{csv_file_path}'")
                    #print(filtered_df)
        
    
class HHPValue:
    def __init__(self, index, adxvma_period):
        self.index = index
        self.adxvma_period = adxvma_period
    
    def get_hhp_value(self):

        hhp = np.max(self.index[-self.adxvma_period-1:])
        #print("HHP:", hhp)
        return hhp

class LLVValue:
    def __init__(self, index, adxvma_period):
        self.index = index
        self.adxvma_period = adxvma_period
    
    def get_llv_data(self):
        llv = np.min(self.index[-self.adxvma_period-1:])
        #print("LLP:", llv)
        return llv

class ATRValue:
    def __init__(self, json_data,period,sorted_df):
        self.json_data = json_data
        self.period = period
        self.sorted_df = sorted_df
        self.atr_values = 0

    def true_range(self, high, low, previous_close):
        return max(high - low, abs(high - previous_close), abs(low - previous_close))

    def average_true_range(self):
        data_list = self.json_data
        data = json.loads(data_list)
        #print(data)
        high = [item['High'] for item in data]
        #print(high)
        low = [item['Low'] for item in data]
        close = [item['Close'] for item in data]
        BarCount = len(high)
        
        # Calculate previous close values
        previous_close = [None]  # Placeholder for the first entry
        DATA_LEN = len(data)
        #print(DATA_LEN)
        previous_close=data[DATA_LEN - 2]['Close']
        
        current_high = data[DATA_LEN - 1]['High']
        current_low = data[DATA_LEN - 1]['Low']
        current_close = data[DATA_LEN - 1]['Close']
        #for i in range(1, len(data)):
            #previous_close.append(data[i-1]['Close'])
    
            
        true_ranges = self.true_range(current_high, current_low, previous_close)
                
        
        #print(true_ranges)
        #self.sorted_df['true_ranges'] = true_ranges
        global_df.reset_index(drop=True, inplace=True)
            
        # Initialize an array to store the boolean mask
        filtered_rows = np.zeros(len(global_df), dtype=bool)
        filtered_rows |= (global_df['ExchangeInstrumentID'] == data[DATA_LEN - 1]['ExchangeInstrumentID']) & (global_df['Date Time'] == data[DATA_LEN - 1]['Date Time'])
        #print(filtered_rows)
        #global_df.loc[filtered_rows, 'true_ranges'] = sorted_df['true_ranges']
        global_df.loc[filtered_rows, 'true_ranges'] = true_ranges
        
        
        #print("ID IS ", data[DATA_LEN - 1]['ExchangeInstrumentID'])
        #atr_values = 0
        exchange_data = global_df[global_df['ExchangeInstrumentID'] == data[DATA_LEN - 1]['ExchangeInstrumentID']]
        sorted_df = exchange_data.sort_values(by='Date Time')
        if len(exchange_data['true_ranges']) == self.period + 1:
            sum_of_true_range = global_df['true_ranges'].sum()
            #print("Total is ", sum_of_true_range)
            self.atr_values = float(sum_of_true_range / self.period)

            #print("ATR values ",self.atr_values)
                    
            # Initialize an array to store the boolean mask
            filtered_rows = np.zeros(len(global_df), dtype=bool)
            filtered_rows |= (global_df['ExchangeInstrumentID'] == data[DATA_LEN - 1]['ExchangeInstrumentID']) & (global_df['Date Time'] == data[DATA_LEN - 1]['Date Time'])
            #print(filtered_rows)
            #global_df.loc[filtered_rows, 'true_ranges'] = sorted_df['true_ranges']
            global_df.loc[filtered_rows, 'atr_values'] = self.atr_values
            
        elif len(exchange_data['true_ranges']) > self.period + 1:
            sort_df_length = len(sorted_df)
        
            last_true_range = sorted_df.iloc[-1]['true_ranges']
            last_adxvma = sorted_df.iloc[-2]['atr_values']

            adxvma_value = last_adxvma * ((self.period - 1) + last_true_range)
            self.atr_values = adxvma_value/self.period
            filtered_rows = np.zeros(len(global_df), dtype=bool)
            filtered_rows |= (global_df['ExchangeInstrumentID'] == data[DATA_LEN - 1]['ExchangeInstrumentID']) & (global_df['Date Time'] == data[DATA_LEN - 1]['Date Time'])

            global_df.loc[filtered_rows, 'atr_values'] = self.atr_values
        
        
        plus_dm = np.where((high - np.roll(high, 1)) > (np.roll(low, 1) - low), np.maximum(high - np.roll(high, 1), 0), 0)    
        #print("PLUS DM ",plus_dm)
        minus_dm = np.where((np.roll(low, 1) - low) > (high - np.roll(high, 1)), np.maximum(np.roll(low, 1) - low, 0), 0)
        #print("MINUS DM ",minus_dm)
        #print("ATR ", self.atr_values)
        tr_ma = np.convolve(self.atr_values, np.ones(self.period), 'valid') / self.period
        #print("TR MA ",tr_ma)
        
        plus_dm_ma = np.convolve(plus_dm, np.ones(self.period), 'valid') / self.period
        #print("PLUS DMMA ",plus_dm_ma)
        minus_dm_ma = np.convolve(minus_dm, np.ones(self.period), 'valid') / self.period
        #print("MINUS DMMA ",minus_dm_ma)
        
        min_length = min(len(plus_dm_ma), len(tr_ma))
        plus_dm_ma = plus_dm_ma[:min_length]
        minus_dm_ma = minus_dm_ma[:min_length]
        tr_ma = tr_ma[:min_length]
        di_plus = (plus_dm_ma / tr_ma) * 100
        #print("di plus ",di_plus)
        di_minus = (minus_dm_ma / tr_ma) * 100
        #print("di_MINUS ",di_minus)
        
        dx = (np.abs(di_plus - di_minus) / (di_plus + di_minus)) * 100
    
    # Calculate ADXVMA
        adxvma = np.convolve(dx, np.linspace(1, 0, self.period), 'valid')
        
        #print("adxvma ", adxvma)
        
        if self.atr_values > 1:
            filtered_rows = np.zeros(len(global_df), dtype=bool)
            filtered_rows |= (global_df['ExchangeInstrumentID'] == data[DATA_LEN - 1]['ExchangeInstrumentID']) & (global_df['Date Time'] == data[DATA_LEN - 1]['Date Time'])
            # print(adxvma[0])
            global_df.loc[filtered_rows, 'adxvma'] = adxvma[0]
            #for i in range(self.period, len(true_ranges)):
                #atr_values.append((atr_values[-1] * (self.period - 1) + true_ranges[i]) / self.period)
        
            #return current_close, previous_close,len(exchange_data['true_ranges']),BarCount

