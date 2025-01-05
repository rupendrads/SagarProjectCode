from venv import logger
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading
import pymysql
from dbutils.pooled_db import PooledDB    
from helpers import Logger
from retrying import retry
import sys
import os

app = Flask(__name__)
socketio = SocketIO(app)
data_counter = 0

logger = Logger('socketPush.txt')
# Configure database connection pool
pool = PooledDB(
    creator=pymysql,
    maxconnections=5,  # Max number of connections to create
    mincached=2,       # Min number of connections to keep in the pool
    maxcached=5,       # Max number of connections to keep in the pool
    maxshared=3,       # Max number of shared connections
    blocking=True,     # Wait for connection if pool is full
    maxusage=None,     # Max number of reuses of a single connection
    setsession=[],     # List of SQL commands to prepare the session
    ping=1,            # Ping the MySQL server to check if it's alive
    host='127.0.0.1',
    user='root',
    password='root',
    database='sagar_dataharvesting',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

@socketio.on('connect')
def handle_connect():
    emit('message', {'data': 'Connected to server'})

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def get_connection():
    return pool.connection()

def read_last_id():
    print(os.path)
    if os.path.exists('D:\\last_id.txt'):        
        with open('D:\\last_id.txt', 'r') as file:
            return int(file.read().strip())
    else:
        return 0

def write_last_id(last_id):
    with open('D:\\last_id.txt', 'w') as file:
        file.write(str(last_id))

def poll_database():
    global data_counter
    last_id = read_last_id()  # Read the last processed ID from file
    while True:
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute("SELECT id,OverallData FROM data_harvesting_20240614 WHERE id > %s ORDER BY ID", (last_id))
                    rows = cursor.fetchall()
                    
                    if rows:
                        last_id = rows[-1]['id']  # Assuming the first column is the ID
                        for row in rows:
                            data_counter += 1 
                            #print(row)
                            logger.log(f'Row : @{row['id']} Counter : @{data_counter}' )
                            #socketio.emit('message', {'data': row})
                            #write_last_id(rows[-1]['id'])  # Write the last processed ID to file
            time.sleep(1)  # Reduce sleep time for more real-time updates
        except pymysql.MySQLError as e:
            print(f"MySQL Error: {e}")
            time.sleep(5)  # Wait before retrying in case of an error
        except Exception as e:
            print(f"Unexpected Error: {e}")
            time.sleep(5)  # Wait before retrying in case of an unexpected error

if __name__ == '__main__':
    threading.Thread(target=poll_database).start()
    socketio.run(app, debug=True)
