# -*- coding: utf-8 -*-
"""
Created on Fri May 24 20:48:45 2024

@author: Admin
"""

import pandas as pd
import numpy as np
import json
from adxv import MAXVALUE,HHPValue,LLVValue,ATRValue
import time
from database import DATABASE
import pandas as pd
import matplotlib.pyplot as plt
# Read the Excel file
import openpyxl
import os
from datetime import datetime, timedelta

period = 3
adxvma_period = 3

k = 1/adxvma_period
db = DATABASE(host='localhost', user='root', password='root', database='sagar_strategy')

# Printing sample_new_data to verify the content
#print(sample_new_data)

# Connect to the database      
db.connect()
initial_time = db.initial_time()
last_time = db.last_time()

print(initial_time)
print(last_time)
#end_time = initial_time
#start_time = initial_time

start_time = initial_time
last_time = "2014-06-01 09:50:18"
end_time = "2014-06-01 02:00:00"
comparison_time = datetime.strptime('2014-06-02 09:50:00', '%Y-%m-%d %H:%M:%S')

#result,start_time,end_time = db.fetch_data(start_time, end_time)
    #print(result)
 
initial_newtime = datetime.strptime(initial_time, '%Y-%m-%d %H:%M:%S')

end_time = start_time
while initial_newtime < comparison_time:
    if (start_time<='2014-06-02 09:00:00'):            
        result,start_time,end_time = db.fetch_data(start_time, end_time)
        OHLC  = MAXVALUE(result)
        OHLC.sortresult(result)


#while start_time <= last_time:
    #result,start_time,end_time = db.fetch_data(start_time, end_time)
    #print(result)
    

    
    
    #OHLC  = MAXVALUE(result)
    #OHLC.sortresult(result)
    #ohlcv_data = OHLC.calculate_ohlcv(result,end_time)
    
    #print(ohlcv_data)
'''
    df_to_append = pd.DataFrame(ohlcv_data)

    # Append the data to an existing Excel file or create a new one if it doesn't exist
    file_path = 'output.xlsx'
    try:
        existing_data = pd.read_excel(file_path)
        updated_data = pd.concat([existing_data, df_to_append], ignore_index=True)
    except FileNotFoundError:
        updated_data = df_to_append

    # Write the updated DataFrame to the Excel file
    updated_data.to_excel(file_path, index=False)
    
    if len(ohlcv_data) > 0: 
    #ATR Function
        atr_cal = ATRValue(ohlcv_data,period)
        atr_values, BarCount, close, previous_close = atr_cal.average_true_range()
        #print("Average True Range (ATR) values:", atr_values)
        #print("Close : ",close)
        #print(BarCount)
    
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
        fractionUp = np.where(isum > 0, np.divide(up, isum, out=np.zeros_like(up), where=isum!=0), 0)
        fractionDown = np.where(isum > 0, np.divide(down, isum, out=np.zeros_like(down), where=isum!=0), 0)
    
        #print("fractionUp:", fractionUp)
        #print("fractionDown:", fractionDown)
    
        ups,downs = max_test.get_ups_downs(fractionUp,fractionDown,BarCount,k)
        #print(ups)
        #print(downs)
    
        ups = np.array(ups)
        downs = np.array(downs)
    
        normDiff = abs(ups - downs);
        normSum = ups + downs;
    
    
        normFraction =  np.where(normSum > 0.0,np.divide(normDiff, normSum, out=np.zeros_like(normDiff), where=normSum!=0), 0) 
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
    
    
        vIndex = np.where((ihhv - illv) > 0.0, np.divide((index - illv), (ihhv - illv), out=np.zeros_like((index - illv)), where=(ihhv - illv)!=0), 0)
    
        #print(vIndex)
    
        adxvma = max_test.get_adxvma(vIndex,close,BarCount,k)
        print("ADXVMA : ", adxvma)

    
    
    
    #df_to_append = pd.DataFrame(ohlcv_data)

    # Append the data to an existing Excel file or create a new one if it doesn't exist
    #file_path = 'output.xlsx'
    #try:
     #   existing_data = pd.read_excel(file_path)
      #  updated_data = pd.concat([existing_data, df_to_append], ignore_index=True)
    #except FileNotFoundError:
        #updated_data = df_to_append

# Write the updated DataFrame to the Excel file
    #updated_data.to_excel(file_path, index=False)
    
    #for data in ohlcv_data:
    #    print()
    #    print("Instrument ID : ", data['ExchangeInstrumentID'] )
    #    print("Open : ", data['Open'])
    #    print("Close : ", data['Close'])
    #    print("High : ", data['High'])
     #   print("Low : ", data['Low'])
    #print("")
    #print("")



#db.fetch_data()

#df = pd.read_excel('data.xlsx')

# Convert DataFrame to JSON
#json_data = df.to_json(orient='records')


'''



