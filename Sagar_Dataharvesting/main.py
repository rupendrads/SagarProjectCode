# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 23:38:49 2024

@author: Admin
"""
import time
import os
import json
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
import mysql
try:
    from index_data_upload_latest import DataProcessor, initialize_log_file, db_config, IndexCreator
except ImportError as e:
    print(f"Error importing DataProcessor: {e}")

try:
    from gdfl_implied_futures import ImpliedFuturesCalculator, db_config
except ImportError as e:
    print(f"Error importing DataProcessor: {e}")
    
from constants import db_config,db_name
    
app = Flask(__name__)
CORS(app)
 
@app.route('/processdata', methods=['POST'])
def get_strategy_name():

   value = None
   data = request.json
   print(data)
   upload_status = data['force_upload']['forceUpload']
   print(f' data :{data}')
   data = data['filePath']
   data = data.replace('/','\\')
   data = data.replace('\\', '\\\\')
   print(f'upload_status {upload_status}')
   if data.endswith('.CSV'):
        file_path = data[:-4] + '.csv'
   data = {'filepath': file_path,'force_upload': upload_status}
   print(type(data))
   print(f' data :{data}')
        # Check if the input is a dictionary
   if not isinstance(data, dict):
       return jsonify({'status': 'error', 'message': 'Expected a dictionary'}), 400

        # Initialize necessary components
   initialize_log_file()
    
   connection = mysql.connector.connect(**db_config)
   cursor = connection.cursor()
   cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
   cursor.close()
   connection.close()
   
   db_config['database'] = db_name
   directory_paths = [
        r'D:\Rupendra\Work\Sagar\uploadGDFL\GFDLNFO_BACKADJUSTED_07062023.csv',
    ]
   print(directory_paths)
       # Instantiate DataProcessor
   index_processor = DataProcessor(directory_paths, db_config)

        # Extract filename and force_upload from the dictionary
   print(f"data is {data}")
   filename = data.get('filepath')
   force_upload = data.get('force_upload')
   print(f"data {data}")
   
   print(f"Processing file: {filename} with force_upload={force_upload}")

    # Call preprocess_data for the file
   value,status = index_processor.preprocess_data(filename, force_upload)
    
    # Instantiate IndexCreator and perform indexing
   index_creator = IndexCreator(db_config)
   index_creator.connect_to_database()
   index_creator.create_indices()
   index_creator.close_database_connection()
   if status == 'success':
    # Return failure response if the status is 'error'
        return jsonify({'Status': 'success', 'Details': value}), 200        
   else:
        # Return success response if the status is 'success'
        return jsonify({'Status': 'error', 'Details': value}), 500
        

@app.route('/upload/impliedfutures', methods=['POST'])
def upload_implied_futures():
   value = None
   data = request.json
   instrument_name = data.get('instrument_name')
   start_date = data.get('start_date')
   end_date = data.get('end_date')
   strike_difference = data.get('strike_difference')
   if not all([instrument_name, start_date, end_date, strike_difference]):
        return jsonify({'error': 'Missing parameters'}), 400

    # Instantiate ImpliedFuturesCalculator with parameters
   calculator = ImpliedFuturesCalculator(instrument_name, start_date, end_date, strike_difference)
   value = calculator.run()
   print(f"value in server")
   print({"Status":'success'})
   if value == "true":
       return jsonify({'Status': 'success'}), 200  
   else:
       return jsonify({'Status': 'error'}), 500  

     
    
if __name__ == '__main__':
    app.run()


