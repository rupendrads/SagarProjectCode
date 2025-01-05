import mysql.connector
import os
import pandas as pd
import warnings
from datetime import datetime
import re
from constants import *
import time
log_file_path = None

def initialize_log_file():
    global log_file_path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_date = datetime.now().date().strftime('%Y-%m-%d')
    log_file_name = f'log_{current_date}.txt'
    log_file_path = os.path.join(script_dir, log_file_name)
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as log_file:
            log_file.write(f'Log file created on {current_date}\n')


def write_to_file(content):
    if log_file_path is None:
        raise RuntimeError("Log file path is not initialized. Call initialize_log_file() first.")
    
    try:
        with open(log_file_path, 'a') as f:
            log_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{log_timestamp} - {content}\n")
    
    except IOError as e:
        print(f"Error writing to file {log_file_path}: {e}")

from datetime import datetime

def log_action(message, log_file="deepak.txt"):
    """
    Logs a message with the current timestamp to the specified log file.
    
    Args:
        message (str): The message to log.
        log_file (str): The path to the log file.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{timestamp} - {message}\n"
    
    with open(log_file, "a") as f:
        f.write(log_message)

class IndexCreator:
    def __init__(self, db_config):
        self.db_config = db_config
        self.db_connection = None

    def connect_to_database(self):
        self.db_connection = mysql.connector.connect(**self.db_config)

    def delete_indices(self):
        if self.db_connection:
            cursor = self.db_connection.cursor()
            try:
                cursor.execute("SHOW TABLES;")
                tables = [table[0] for table in cursor.fetchall()]
                #print(f"TABLES ARE : {tables}")
                if not tables:
                    print("No tables found in the database.")
                else:
                    for table in tables:
                        if table != "upload_status":
                            cursor.execute(f"SHOW INDEX FROM {table};")
                            indexes = cursor.fetchall()
                            #print(f"index is {indexes}")
                            
                            for index in indexes:
                                index_name = index[2]  # The index name is in the third column
                                if index_name != 'PRIMARY':
                                    # If it's a primary key, drop it using ALTER TABLE
                                    drop_primary_command = f"ALTER TABLE {table} DROP INDEX {index_name}"
                                    try:
                                        cursor.execute(drop_primary_command)
                                        print(f"{index_name} dropped from table '{table}'.")
                                    except mysql.connector.Error as err:
                                        print(f"Error dropping primary key from table '{table}': {err}")
                                   
                    # Commit the changes
                    self.db_connection.commit()
            except mysql.connector.Error as err:
                print(f"Error retrieving indexes: {err}")
            finally:
                cursor.close()
    def close_database_connection(self):
        if self.db_connection:
            self.db_connection.close()

    def create_indices(self):
        if self.db_connection:
            cursor = self.db_connection.cursor()
            try:
                cursor.execute("SHOW TABLES;")
                tables = [table[0] for table in cursor.fetchall()]
                for table in tables:
                    if table != 'upload_status':
                        self.create_index(cursor, table, 'timestamp')
                        self.create_index(cursor, table, 'symbol')
                        self.create_index(cursor, table, 'type')
            except mysql.connector.Error as err:
                # print(f"Error creating indices: {err}")
                pass
            finally:
                cursor.close()
                self.db_connection.close()

    def create_index(self, cursor, table_name, column_name):
        index_name = f"idx_{table_name}_{column_name}"
        try:
            cursor.execute(f"CREATE INDEX {index_name} ON {table_name}({column_name})")
            print(f"Index '{index_name}' created on column '{column_name}' in table '{table_name}'.")
            #write_to_file(f"{index_name}' created on column '{column_name}' in table '{table_name}'.")
        except mysql.connector.Error as err:
            # print(f"Error creating index on column '{column_name}' in table '{table_name}': {err}")
            pass


class DataProcessor:
    def __init__(self, directory_paths, db_config):
        self.directory_paths = directory_paths
        self.db_config = db_config
        self.error_log_file = "error_log.txt"
        self.db_connection = None  
        self.total_files_processed = 0
        self.total_files_uploaded = 0
        self.total_rows_updated = 0
        self.df_count = 0

    def connect_to_database(self):
        self.db_connection = mysql.connector.connect(**self.db_config)

    def close_database_connection(self):
        if self.db_connection:
            self.db_connection.close()

    def count_and_list_tables(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_count = len(tables)
        table_names = [table[0] for table in tables]
        return table_count, table_names

    def create_upload_status_table(self):
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS upload_status (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                file_name VARCHAR(255),
                                upload_count INT,
                                total_files_processed INT,
                                status BOOLEAN,
                                remarks TEXT,
                                upload_time DATETIME
                            )''')
            self.db_connection.commit()

    def check_upload_status(self, file_name):
        print(f'check_upload_status  : {self.db_connection}')
        if self.db_connection:
            cursor = None
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT status FROM upload_status WHERE file_name=%s", (file_name,))
                result = cursor.fetchall() 
                # print(f'result  : {result}')
                return result[0] if result else None
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                return None
            finally:
                if cursor is not None:
                    try:
                        print('Attempting to close cursor...')
                        cursor.close()  # Attempt to close the cursor
                        print('Cursor closed successfully.')
                    except mysql.connector.Error as close_err:
                        print(f"Error while closing cursor: {close_err}")
                print('finally')            
        return None
    
    # def check_upload_count(self, file_name):
    #     if self.db_connection:
    #         try:
    #             cursor = self.db_connection.cursor()
    #             cursor.execute("SELECT upload_count FROM upload_status WHERE file_name=%s", (file_name,))
    #             result = cursor.fetchone()
    #         finally:
    #             cursor.close()
    #         return result[0] if result else None
    #     return None
    def check_upload_count(self, file_name):
        if self.db_connection:
            cursor = None
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT upload_count FROM upload_status WHERE file_name=%s", (file_name,))
                result = cursor.fetchone()
                # Ensure the cursor is fully read
                cursor.fetchall()  # This ensures that if there's any additional unread result, it's fetched
            except mysql.connector.errors.InternalError as e:
                print(f"Error fetching upload count: {e}")
            finally:
                if cursor:
                    cursor.close()
            return result[0] if result else None
        return None


    def update_upload_status(self, file_name, upload_count, total_files_processed, status, remarks, upload_time):
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("INSERT INTO upload_status (file_name, upload_count, total_files_processed, status, remarks, upload_time) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (file_name, upload_count, total_files_processed, status, remarks, upload_time))
            self.db_connection.commit()

    # def get_upload_status(self,file_name,message):
    #     if self.db_connection:
    #         cursor = self.db_connection.cursor()
    #         query = "SELECT upload_count, total_files_processed, upload_time FROM upload_status WHERE file_name = %s AND upload_count != 0 LIMIT 1"
    #         print(f"query : {query}")
    #         cursor.execute(query, (file_name,))
            
    #         # Fetch the result from the query
    #         result = cursor.fetchone()
        
    #         if result:
    #             upload_count, total_files_processed, upload_time = result
    #             value = f"{message}, Details : Upload Count: {upload_count},Total Files Processed: {total_files_processed},Upload Time: {upload_time}"
    #             # Print the values
    #             write_to_file(message)
    #             return value,upload_count
    #         else:
    #             value ="No data found"
    #             print("No data found")
    #             upload_count = ""
    #             write_to_file("No data found")
    #             return value,upload_count
    def get_upload_status(self, file_name, message):
        if self.db_connection:
            cursor = None
            try:
                cursor = self.db_connection.cursor()
                # Modify query to order by upload_time in descending order
                query = """
                    SELECT upload_count, total_files_processed, upload_time 
                    FROM upload_status 
                    WHERE file_name = %s AND upload_count != 0 
                    ORDER BY upload_time DESC 
                    LIMIT 1
                """
                cursor.execute(query, (file_name,))
                
                result = cursor.fetchone()
            
                if result:
                    upload_count, total_files_processed, upload_time = result
                    value = f"{message}, Details : Upload Count: {upload_count}, Total Files Processed: {total_files_processed}, Upload Time: {upload_time}"
                    write_to_file(message)
                    return value, upload_count
                else:
                    value = "No data found"
                    print("No data found")
                    upload_count = ""
                    write_to_file("No data found")
                    return value, upload_count
            finally:
                if cursor:
                    cursor.close()
        return "Database connection failed", ""

                
    def delete_all_data(self,file_name):
        print(file_name)
        if self.db_connection:
            cursor = self.db_connection.cursor()
            query = "SHOW TABLES"
            cursor.execute(query)
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                if table_name != 'upload_status':
                    #print(table_name)
                    query = f"DELETE FROM `{table_name}` WHERE provider=%s"
                    cursor.execute(query, (file_name,))
            print("Existing data is deleted")


    def read_csv(self, file_path):
        return pd.read_csv(file_path)
    
    def process_data(self,file_path,force_upload):
        print('process_data')
        if log_file_path is None:
            initialize_log_file()
        print('initialize_log_file')
        with open(self.error_log_file, "a") as error_log:
            file_exists = os.path.exists(file_path)
            file_name = os.path.basename(file_path)
            print('with open(self.error_log_file, "a") as error_log')
            print(f'file_exists : {file_exists}')
            if file_exists:
                write_to_file(f"File exists: {file_name}")
                self.total_files_processed += 1
                #file_path = os.path.join(month_dir_path, file_name)
                upload_status = self.check_upload_status(file_name)
                print(f"upload status is {upload_status}")
                
                if force_upload or upload_status is None:
                    print(f"Reading file: {file_path}")
                    try:
                        df = self.read_csv(file_path)
                        csv_count = len(file_path)
                        print(f"csv_count: {csv_count}")
                        df.columns = df.columns.str.replace(' ', '')
                        # solution for date column
                        df.columns = df.columns.str.lower()
                        df = df.rename(columns={
                            'ticker': 'symbol',
                            'date': 'date',
                             'time': 'time',
                             'open': 'open',
                             'high': 'high',
                             'low': 'low',
                             'close': 'close',
                             'volume': 'volume',
                             'openinterest': 'oi'
                             })
                        #fix time issue
                        try:
                            df['date'] = df['date'].str.split(' ').str[0]
                            df.loc[df.time.str.len() != 8, 'time'] = df.loc[df.time.str.len() != 8, 'time'].str.split(' ').str[1] + ":59"
                            df['date'] = df['date'].str.replace(r'[-/]', '/', regex=True)
                        except Exception as e:
                            print(f"error occured process time \n {df}")
                        timestamp_pattern = r'\d{2}/\d{2}/\d{4}'
                        if df['date'].str.match(timestamp_pattern).any():
                            df['timestamp'] = df['date'] + ' ' + df['time']
                            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y %H:%M:%S')
                            print("if block \n {df}")          

                        df['timestamp'] = df['timestamp'].dt.floor('min')
                                        
                        df.drop(columns=['time','date'], inplace=True)
                        df.columns = map(str.lower, df.columns)
                        value,status = self.process_dataframe(df, file_path, force_upload,csv_count)
                        print('Rupendra')
                        if force_upload:
                            # self.update_upload_status(os.path.basename(file_path), self.df_count, self.total_rows_updated, True, "File reuploaded successfully.", datetime.now())
                            file_name = os.path.basename(file_path)
                            message = "{} reuploaded successfully.".format(file_name)
                            #status = "success"
                            value,upload_count = self.get_upload_status(file_name,message)
                            # print(value, upload_count)
                            if upload_count == csv_count:
                                status = "success"
                            else:
                                status = "error"
                    except Exception as e:
                        write_to_file("Error processing file {}: {}, process_data block\n".format(file_name, str(e)))
                        error_log.write(f"Error processing file {file_path}: {str(e)}, process_data block\n")
                        value = "Error processing file {}: {}, process_data block\n".format(file_name, str(e))
                        status = "error"
                        self.update_upload_status(file_name, self.df_count, self.total_rows_updated, False, str(e), datetime.now())
                else:

                    print(f"Skipping file {file_name}: Already uploaded.")
                    message = "Skipping file {}: Already uploaded.".format(file_name)
                    write_to_file(message)
                    value = self.get_upload_status(file_name,message)
                    upload_count = self.check_upload_count(file_name)
                    df = self.read_csv(file_path)
                    csv_count = len(df)
                    print(f"upload count {upload_count}, csv count {csv_count}")
                    if upload_count == csv_count:
                    # self.update_upload_status(file_name, 0, 0, False, "File already uploaded.", datetime.now())
                        status = "success"
                    else:
                        status = "error"
                    self.total_files_uploaded += 1
                    self.update_upload_status(file_name, 0, 0, False, "File Already Uploaded", datetime.now())
                    

                print(f"Total files processed: {self.total_files_processed}")
                write_to_file(f"Total files processed: {self.total_files_processed}")
                print(f"Total files uploaded: {self.total_files_uploaded}")
                write_to_file(f"Total files uploaded: {self.total_files_uploaded}")
                
            else:
                write_to_file(f"File does not exist: {file_name}")
                value = f"File does not exist: {file_name}"
                status = "error"
                
        return value,status
        
    '''
    def process_data(self,filename,force_upload):
        if log_file_path is None:
            initialize_log_file()
        
        with open(self.error_log_file, "a") as error_log:
            for directory_path in self.directory_paths:
                for month_dir in os.listdir(directory_path):
                    month_dir_path = os.path.join(directory_path, month_dir)
                    if os.path.isdir(month_dir_path):
                        file_path = None
                        for file_name in os.listdir(month_dir_path):
                            if file_name.endswith('.csv'):
                                if file_name == filename:
                                    #self.delete_all_data(file_name)
                                    self.total_files_processed += 1
                                    file_path = os.path.join(month_dir_path, file_name)
                                    upload_status = self.check_upload_status(file_name)
                                    if (upload_status is None or not upload_status) or force_upload:
                                        print(f"Reading file: {file_path}")
                                        try:
                                                df = self.read_csv(file_path)
                                                df.columns = df.columns.str.replace(' ', '')
                                                df = df.rename(columns={
                                                    'Ticker': 'symbol',
                                                    'Date': 'date',
                                                    'Time': 'time',
                                                    'Open': 'open',
                                                    'High': 'high',
                                                    'Low': 'low',
                                                    'Close': 'close',
                                                    'Volume': 'volume',
                                                    'OpenInterest': 'oi'
                                                })
                                                timestamp_pattern = r'\d{2}/\d{2}/\d{4}'
    
                                                if df['date'].str.match(timestamp_pattern).any():
                                                    df['timestamp'] = df['date'] + ' ' + df['time']
                                                    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y %H:%M:%S')
                                                
                                                else:
                                                    df['timestamp'] = df.date + ' ' + df.time
                                                    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y %H:%M:%S')
                                                df['timestamp'] = df['timestamp'].dt.floor('min')
                                                
                                                df.drop(columns=['time','date'], inplace=True)
                                                df.columns = map(str.lower, df.columns)
                                                self.process_dataframe(df, file_path, force_upload)
                                                if force_upload:
                                                    self.update_upload_status(os.path.basename(file_path), self.df_count, self.total_rows_updated, True, "File reuploaded successfully.", datetime.now())
                                                    file_name = os.path.basename(file_path)
                                                    message = "{} reuploaded successfully.".format(file_name)
                                                    self.get_upload_status(file_name,message)
                                        except Exception as e:
                                            write_to_file("Error processing file {}: {}, process_data block\n".format(file_name, str(e)))
                                            error_log.write(f"Error processing file {file_path}: {str(e)}, process_data block\n")
                                            self.update_upload_status(file_name, self.df_count, self.total_rows_updated, False, str(e), datetime.now())
                                    else:
                                        print(f"Skipping file {file_name}: Already uploaded.")
                                        message = "Skipping file {}: Already uploaded.".format(file_name)
                                        write_to_file(message)
                                        #write_to_file(f"Skipping file {file_name}: Already uploaded.")
                                        print(file_name)
                                        self.update_upload_status(file_name, 0, 0, False, "File already uploaded.", datetime.now())
                                        self.get_upload_status(file_name,message)
                                        self.total_files_uploaded += 1
                                else:
                                    error_log.write(f"File format mismatch: {file_path}\n")
                            else:
                                message = "{} not present in the directory".format(filename)
                                write_to_file(message)

        print(f"Total files processed: {self.total_files_processed}")
        write_to_file(f"Total files processed: {self.total_files_processed}")
        print(f"Total files uploaded: {self.total_files_uploaded}")
        write_to_file(f"Total files uploaded: {self.total_files_uploaded}")
    '''    
    
    def extract_symbol_details(self, input_string):
        pattern = re.compile(r'(.+?)(\d{2}[A-Z]{3}\d{2})(.+)')
        match = pattern.search(input_string)
        if match:
            instrument_symbol = match.group(1).strip().replace('-', '_').replace('&', '_')  
            strike_type = match.group(3).strip()
            strike_type = strike_type[:-4]
            strike = strike_type[:-2]
            type_ = strike_type[-2:]
            matched_date = match.group(2)
            date_object = datetime.strptime(matched_date, '%d%b%y').date()
            if strike=='F':
                strike=None
                type_='FUT'
                
        else:
            pattern = re.compile(r'^(.+?)-(I{1,3})\.NFO$')
            match = pattern.match(input_string)
            instrument_symbol = match.group(1).replace('-', '_').replace('&', '_')  
            date_object = match.group(2)
            type_ = 'FUT'
            strike = None
        return instrument_symbol, date_object, strike, type_

    def process_dataframe(self, df, file_path, force_upload,csv_count):
        try:
            df[['instrument_symbol', 'expiry', 'strike', 'type']] = df['symbol'].apply(
                lambda x: pd.Series(self.extract_symbol_details(x)))
            df.reset_index(drop=True, inplace=True)
            futures_data = df
            self.df_count = len(df)
            if force_upload:
                log_action("Force upload is True. Deleting existing data for file")
                self.delete_existing_data(file_path, df)
                log_action("deleted existing data")
                # index_creator = IndexCreator(db_config)
                # index_creator.connect_to_database()
                # log_action("Connected to database for index deletion")
                # index_creator.delete_indices()
                # log_action("index deletion completed")
                # index_creator.close_database_connection()
            # print("self.delete_existing_data")
            operation_status = self.insert_data_to_database(futures_data, file_name=file_path)
            log_action("finished inserting in db")
            print(f"operation_status : {operation_status}")
            if operation_status:
                self.update_upload_status(file_name, 0, 0, False, operation_status, datetime.now())
                status = False
                self.total_files_processed+=1
                return operation_status, status

            if not force_upload:
                self.update_upload_status(os.path.basename(file_path), self.df_count, self.total_rows_updated, True, "File uploaded successfully.", datetime.now())
                file_name = os.path.basename(file_path)
                message = "{} uploaded successfully.".format(file_name)
                
                value,upload_count = self.get_upload_status(file_name,message)
                if upload_count == csv_count:
                    status = "success"
                else:
                    status = "error"

            if force_upload:
                print(f"force_upload")
                self.update_upload_status(os.path.basename(file_path), self.df_count, self.df_count, True, "File  Re uploaded successfully.", datetime.now())
                file_name =  os.path.basename(file_path)
                message = "{} Re uploaded successfully.".format(file_name)
                
                value,upload_count = self.get_upload_status(file_name,message)
                print(f" value :{value}  upload_count :{upload_count}")
                if upload_count == csv_count:
                    status = "success"
                else:
                    status = "error"
            self.total_files_uploaded += 1
            return value,status
        except Exception as e:
            value = "{} couldn't upload".format(file_path)
            write_to_file("{} couldn't upload".format(file_path))
            with open(self.error_log_file, "a") as error_log:
                error_log.write(f"Error processing DataFrame: {str(e)} in {file_path}, process block\n")
                print(f'Error processing DataFrame: {str(e)} in {file_path}, process block\n')
                status ="error"
                self.update_upload_status(os.path.basename(file_path), self.df_count, self.total_rows_updated, False, "File couldn't upload.", datetime.now())
            return value,status
                
    def insert_data_to_database(self, df, file_name):
        try:
            print("Starting insertion")
            log_action("inside insert_data_to_database block")
            self.total_rows_updated = 0
            if self.db_connection:
                cursor = self.db_connection.cursor()
                year = re.search(r'(\d{4})\.csv$', file_name).group(1)

                for instrument_symbol, symbol_data in df.groupby('instrument_symbol'):
                    print(f"File path name is {file_name} and year is {year}")
                    
                    table_name = f"{instrument_symbol}_{year}"
                    print(f"Table name: {table_name}") 

                    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                    table_exists = cursor.fetchall()
                    print(f"Table exists: {table_exists}")

                    if not table_exists:
                        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                                            id INT AUTO_INCREMENT PRIMARY KEY,
                                            timestamp DATETIME,
                                            symbol VARCHAR(40),
                                            expiry DATE,
                                            type VARCHAR(4),
                                            strike FLOAT,
                                            open FLOAT,
                                            high FLOAT,
                                            low FLOAT,
                                            close FLOAT,
                                            oi INT,
                                            volume INT,
                                            provider VARCHAR(100),
                                            upload_time DATETIME,
                                            implied_futures_weekly FLOAT,
                                            implied_futures_monthly FLOAT
                                        )''')
                        self.db_connection.commit()

                    rows_to_insert = []
                    fut_rows_to_insert = []

                    for index, row in symbol_data.iterrows():
                        timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                        expiry = row['expiry']

                        if expiry in ['I', 'II', 'III']:
                            fut_table_name = f"{instrument_symbol}_FUT"
                            cursor.execute(f"SHOW TABLES LIKE '{fut_table_name}'")
                            table_exists = cursor.fetchall()

                            if not table_exists:
                                cursor.execute(f'''CREATE TABLE IF NOT EXISTS {fut_table_name} (
                                                id INT AUTO_INCREMENT PRIMARY KEY,
                                                timestamp DATETIME,
                                                symbol VARCHAR(40),
                                                expiry VARCHAR(3),
                                                type VARCHAR(40),
                                                strike FLOAT,
                                                open FLOAT,
                                                high FLOAT,
                                                low FLOAT,
                                                close FLOAT,
                                                oi INT,
                                                volume INT,
                                                provider VARCHAR(100),
                                                upload_time DATETIME,
                                                implied_futures_weekly FLOAT,
                                                implied_futures_monthly FLOAT
                                            )''')
                                self.db_connection.commit()

                            # Collecting rows for future table insertion
                            fut_rows_to_insert.append((
                                timestamp_str, row['symbol'], expiry, row['type'], row['strike'],
                                row['open'], row['high'], row['low'], row['close'], row['oi'],
                                row['volume'], os.path.basename(file_name), datetime.now(), None, None
                            ))
                        else:
                            # Collecting rows for main table insertion
                            rows_to_insert.append((
                                timestamp_str, row['symbol'], expiry, row['type'], row['strike'],
                                row['open'], row['high'], row['low'], row['close'], row['oi'],
                                row['volume'], os.path.basename(file_name), datetime.now(), None, None
                            ))
                    
                    # Bulk insert for FUT table if any rows are collected
                    if fut_rows_to_insert:
                        fut_start_time = time.time()
                        cursor.executemany(f'''
                            INSERT INTO {fut_table_name} 
                            (timestamp, symbol, expiry, type, strike, open, high, low, close, oi, volume, provider, upload_time, implied_futures_weekly, implied_futures_monthly) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', fut_rows_to_insert)
                        fut_end_time = time.time()
                        log_action(f"time taken for {fut_table_name} insertion is {fut_end_time - fut_start_time} seconds")
                    # Bulk insert for main table
                    if rows_to_insert:
                        opt_start_time = time.time()
                        cursor.executemany(f'''
                            INSERT INTO {table_name} 
                            (timestamp, symbol, expiry, type, strike, open, high, low, close, oi, volume, provider, upload_time, implied_futures_weekly, implied_futures_monthly) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', rows_to_insert)
                        opt_end_time = time.time()
                        log_action(f"time taken for {table_name} insertion is {opt_end_time - opt_start_time} seconds")
                    # Update the total rows updated
                    self.total_rows_updated += len(rows_to_insert) + len(fut_rows_to_insert)
                    
                self.db_connection.commit()
                print(f"Total rows updated: {self.total_rows_updated}")
                return False
                
        except Exception as e:
            message = f"Error occurred in {row['instrument_symbol']}, str{e}, end of sentence"
            print(message)
            return message  
    



    # def delete_existing_data(self, file_path, df):
    #     print("existing data is being deleted") 
    #     delete_queries=[]
    #     if self.db_connection:
    #         file_name = os.path.basename(file_path)
    #         date_match = re.search(r'(\d{2})(\d{2})(\d{4})', file_name)
    #         if date_match:
    #             day, month, year = date_match.groups()
    #         file_date = f"{year}-{month}-{day}"
    #         cursor = self.db_connection.cursor()
    #         for instrument_symbol, symbol_data in df.groupby('instrument_symbol'):
    #             # yearmatch = re.search(r'(\d{4})', file_path)
    #             year = re.search(r'(\d{4})\.csv$', file_name).group(1) #yearmatch.group(1)
    #             print(year)
    #             table_name = f"{instrument_symbol}_{year}"
    #             # print("attempting to delete from table {table_name}")
    #             # cursor.execute(f"SELECT * FROM {table_name} WHERE date(timestamp)=%s", (file_date,))
    #             # deleted_rows = cursor.fetchall()
    #             #cursor.execute(f"DELETE FROM {table_name} WHERE date(timestamp)=%s", (file_date,))
    #             delete_queries.append(f"DELETE FROM {table_name} WHERE date(timestamp)='{file_date}'")
    #             fut_table_name = f"{instrument_symbol}_FUT"
    #             # cursor.execute(f"SELECT * FROM {fut_table_name} WHERE date(timestamp)=%s", (file_date,))
    #             # deleted_rows_fut = cursor.fetchall()
    #             #cursor.execute(f"DELETE FROM {fut_table_name} WHERE date(timestamp)=%s", (file_date,))
    #             #print(f"Deleted  rows from {table_name} and  {fut_table_name} where date(timestamp) is {file_date}")
    #             delete_queries.append(f"DELETE FROM {fut_table_name} WHERE date(timestamp)='{file_date}'")
    #             # print(f"existing data is deleted from Table {table_name} and row {deleted_rows} and file ".format(file_name) )
    #             # write_to_file("existing data is deleted from Table and file  ")
            
    #         combined_delete_query = "; ".join(delete_queries)
    #         print(combined_delete_query)
    #         try:
    #             for query in delete_queries:
    #                 cursor.execute(query)

    #             # Commit the transaction
    #             self.db_connection.commit()
    #         except mysql.connector.Error as err:
    #             print(f"Error: {err}")
    #             self.db_connection.rollback() 
    #         finally:
    #             cursor.close()  
    #         print("Database connection is not available.")
    def delete_existing_data(self, file_path, df):
        print("Existing data is being deleted") 
        if self.db_connection:
            file_name = os.path.basename(file_path)
            date_match = re.search(r'(\d{2})(\d{2})(\d{4})', file_name)
            if date_match:
                day, month, year = date_match.groups()
            file_date = f"{year}-{month}-{day}"
            cursor = self.db_connection.cursor()
            
            try:
                for instrument_symbol, symbol_data in df.groupby('instrument_symbol'):
                    year = re.search(r'(\d{4})\.csv$', file_name).group(1)
                    table_name = f"{instrument_symbol}_{year}"
                    fut_table_name = f"{instrument_symbol}_FUT"

                    # Delete from the main table
                    delete_query_main = f"DELETE FROM {table_name} WHERE date(timestamp)='{file_date}'"
                    cursor.execute(delete_query_main)
                    print(f"Deleted data from table: {table_name}")

                    # Delete from the futures table
                    delete_query_fut = f"DELETE FROM {fut_table_name} WHERE date(timestamp)='{file_date}'"
                    cursor.execute(delete_query_fut)
                    print(f"Deleted data from table: {fut_table_name}")

                # Commit the transaction after all deletions
                self.db_connection.commit()
                print("All data deletions successful.")
            
            except Exception as e:
                # Rollback if any error occurs
                self.db_connection.rollback()
                print(f"An error occurred during deletion: {e}")
            
            finally:
                cursor.close()

        
    def preprocess_data(self,filename,force_upload):
        self.connect_to_database()
        print('Db Connected')
        self.create_upload_status_table()
        print('create_upload_status_table')
        value,status = self.process_data(filename,force_upload)

        self.close_database_connection() 
        return value,status


    
    


