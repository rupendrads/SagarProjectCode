import logging
import json
import datetime
import pytz
from flask import Flask
from flask_socketio import SocketIO, emit
import time
import pymysql
from dbutils.pooled_db import PooledDB
from retrying import retry
import os
from constants import *

# Flask app and socket setup
app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')
data_counter: int = 0

# Logging configuration
logging.basicConfig(filename='socketPush.txt', level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection pool configuration using pymysql and PooledDB
pool: PooledDB = PooledDB(
    creator=pymysql,
    maxconnections=5,
    mincached=2,
    maxcached=5,
    maxshared=3,
    blocking=True,
    maxusage=None,
    setsession=[],
    ping=1,
    host=host,
    user=user,
    password=password,
    database=database,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Function to handle new client connection to the socket
@socketio.on('connect')
def handle_connect() -> None:
    """Handles a new client connection and sends a confirmation message."""
    emit('message', {'data': 'Connected to server'})

# Function to retry getting a connection from the connection pool with exponential backoff
@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def get_connection() -> pymysql.connections.Connection:
    """Fetch a new database connection from the connection pool with retries."""
    return pool.connection()

# Constants for file name where the last processed ID is stored
LAST_ID_FILE = 'last_id.txt'

def read_last_id() -> int:
    """Reads the last processed ID from the file. Returns 0 if the file does not exist."""
    if os.path.exists(LAST_ID_FILE):
        with open(LAST_ID_FILE, 'r') as file:
            return int(file.read().strip())
    return 0

def write_last_id(last_id: int) -> None:
    """Writes the last processed ID to the file."""
    with open(LAST_ID_FILE, 'w') as file:
        file.write(str(last_id))

def poll_database(data_per_minute: int = None) -> None:
    """
    Polls the database for new data and pushes it through the socket.

    If data_per_minute is provided, it limits the number of messages sent per minute. 
    Otherwise, messages are sent based on database timestamps.
    """
    global data_counter
    last_id: int = read_last_id()
    previous_adjusted_time: datetime.datetime = None

    # Calculate the interval in seconds for each data push
    interval_per_data = 60.0 / data_per_minute if data_per_minute else None

    # Variables for timing and controlling push rate
    start_time = time.monotonic()
    pushed_count = 0  # Track how many rows are pushed each minute

    while True:
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"SELECT id, OverallData FROM {table_name} WHERE id > %s ORDER BY id",
                        (last_id,)
                    )
                    rows = cursor.fetchall()

                    if rows:
                        for row in rows:
                            overall_data = json.loads(row['OverallData'])
                            last_update_time = datetime.datetime.fromtimestamp(
                                overall_data['LastUpdateTime'],
                                tz=pytz.UTC
                            )
                            adjusted_time = last_update_time + datetime.timedelta(days=(365 * 10) + 2)

                            if data_per_minute:
                                current_time = time.monotonic()
                                elapsed_time = current_time - start_time

                                if elapsed_time >= 60:
                                    # logger.info(f"Pushed {pushed_count} data points in the last minute.")
                                    print(f"Pushed {pushed_count} data points in the last minute.")
                                    pushed_count = 0
                                    start_time = current_time  # Reset the timer for the next minute

                                # Send the data
                                socketio.emit('message', {'data': row})
                                data_counter += 1
                                pushed_count += 1
                                # logger.info(f"ID: {row['id']}, Time: {adjusted_time}")
                                # print(f'Data: {row}')
                                write_last_id(row['id'])
                                last_id = row['id']

                                # Calculate the exact sleep time for precision
                                elapsed_time_for_row = time.monotonic() - current_time
                                sleep_time = max(0, interval_per_data - elapsed_time_for_row)
                                time.sleep(sleep_time)
                            else:
                                # Handle normal time-based pushing
                                if previous_adjusted_time is not None:
                                    time_diff = (adjusted_time - previous_adjusted_time).total_seconds()
                                    if time_diff > 0:
                                        time.sleep(time_diff)
                                previous_adjusted_time = adjusted_time

                                socketio.emit('message', {'data': row})
                                data_counter += 1
                                # logger.info(f"ID: {row['id']}, Time: {adjusted_time}")
                                # print(f'Data: {row}')
                                write_last_id(row['id'])
                                last_id = row['id']
                    else:
                        time.sleep(1)

        except pymysql.MySQLError as e:
            logger.error(f"MySQL Error: {e}")
            print(e)
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            print(e)
            time.sleep(5)


if __name__ == '__main__':
    if MODE == 'database_time':
        socketio.start_background_task(poll_database)
    elif MODE == 'data_per_minute':
        socketio.start_background_task(poll_database, data_per_minute=DATA_PER_MINUTE)

    socketio.run(app, debug=True, port=5001, use_reloader=False)
