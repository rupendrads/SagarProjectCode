# -*- coding: utf-8 -*-
"""
Created on Wed May 29 00:43:25 2024

@author: Admin
"""

import mysql.connector
import time
import json
import datetime

# Function to establish a connection to the MySQL database
class DATABASE:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Successfully connected to the database")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            
    def initial_time(self):
        cursor = self.connection.cursor(dictionary=True)
        query = """SELECT LastUpdateTime
                FROM sagar_dataharvesting.data_harvesting_20240531 
                order by Id asc 
                LIMIT 1;"""
        cursor.execute(query)
        result = cursor.fetchone()  # Use fetchone() to retrieve a single row
        cursor.close()
        #print(result)
        time_value = result['LastUpdateTime']
        #print(time_value)
        initial = str(time_value)
        return initial

    
    def last_time(self):
        cursor = self.connection.cursor(dictionary=True)
        query = """SELECT LastUpdateTime
                FROM sagar_dataharvesting.data_harvesting_20240531 
                order by Id desc 
                LIMIT 1;"""
        cursor.execute(query)
        result = cursor.fetchone()  # Use fetchone() to retrieve a single row
        cursor.close()
        #print(result)
        time_value = result['LastUpdateTime']
        #(time_value)
        last_time = str(time_value)
        return last_time

    def fetch_data(self,start_time, end_time):
        end_time_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    
        end_time_dt += datetime.timedelta(minutes=1)

        end_time = end_time_dt.strftime('%Y-%m-%d %H:%M:%S')
        print("Start time : ",start_time)
        print("End time : ",end_time)
        
        cursor = self.connection.cursor(dictionary=True)
        query = """SELECT Id, ExchangeInstrumentID, LastTradedPrice, LastUpdateTime
                FROM sagar_dataharvesting.data_harvesting_20240531 
                WHERE LastUpdateTime >= %s AND LastUpdateTime <= %s"""
                
    # Execute the query with parameters
        cursor.execute(query, (start_time, end_time))
        results = cursor.fetchall()
        cursor.close()
        start_time = end_time
       
        #start_time_data = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        return results, start_time, end_time

    def continuously_fetch_data(self, interval):
        try:
            while True:
                data = self.fetch_data()
                # You can convert the data to JSON here if needed
                json_data = json.dumps(data, indent=4)
                print(json_data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Continuous data fetching stopped.")
        finally:
            self.close()

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Connection to the database closed.")