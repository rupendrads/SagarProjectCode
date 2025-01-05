# # consumer.py

# import socketio
# import json
# import threading
# import time

# # Create a Socket.IO client instance
# sio = socketio.Client()

# # Global counters and timing variables
# data_counter = 0
# messages_received_in_current_minute = 0
# lock = threading.Lock()  # To ensure thread-safe operations on shared variables

# # Define event handlers
# @sio.event
# def connect():
#     print('Connected to server')

# @sio.event
# def disconnect():
#     print('Disconnected from server')

# @sio.on('message')
# def handle_message(data):
#     global data_counter, messages_received_in_current_minute
#     with lock:
#         data_counter += 1
#         messages_received_in_current_minute += 1
#     # print(f'Data received ({data_counter}): {data}')
    
#     # Process the data as needed
#     process_data(data)

# def process_data(data):
#     """
#     Function to process the data received from the server.
#     You can customize this function to perform any processing you need.
#     """
#     try:
#         # Access the 'data' key from the received message
#         row = data.get('data')
#         if row:
#             row_id = row.get('id')
#             overall_data_json = row.get('OverallData')
            
#             # If OverallData is a JSON string, parse it
#             if isinstance(overall_data_json, str):
#                 overall_data = json.loads(overall_data_json)
#             else:
#                 overall_data = overall_data_json
            
#             # Extract specific fields from overall_data
#             last_update_time = overall_data.get('LastUpdateTime')
#             # Perform any additional processing here
            
#             # For demonstration, print the extracted data
#             # print(f'Row ID: {row_id}')
            
#     except Exception as e:
#         print(f'Error processing data: {e}')

# def print_messages_per_minute():
#     global messages_received_in_current_minute
#     while True:
#         time.sleep(60)  # Wait for one minute
#         with lock:
#             print(f"Messages received in the last minute: {messages_received_in_current_minute}")
#             messages_received_in_current_minute = 0  # Reset the counter for the next minute

# if __name__ == '__main__':
#     try:
#         # Start the messages per minute printer thread
#         threading.Thread(target=print_messages_per_minute, daemon=True).start()
        
#         # Connect to the Socket.IO server
#         sio.connect('http://localhost:5001')
#         # Wait for events
#         sio.wait()
#     except Exception as e:
#         print(f'An error occurred: {e}')



import socketio
import json
import threading
import time

# Create a Socket.IO client instance
sio = socketio.Client()

# Global counters and timing variables
data_counter = 0
messages_received_in_current_minute = 0
lock = threading.Lock()  # To ensure thread-safe operations on shared variables

# Define event handlers
@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('message')
def handle_message(data):
    global data_counter, messages_received_in_current_minute
    with lock:
        data_counter += 1
        messages_received_in_current_minute += 1
    # print(f'Data received ({data_counter}): {data}')
    
    # Process the data as needed
    process_data(data)

def process_data(data):
    """
    Function to process the data received from the server.
    You can customize this function to perform any processing you need.
    """
    try:
        # Access the 'data' key from the received message
        row = data.get('data')
        if row:
            row_id = row.get('id')
            overall_data_json = row.get('OverallData')
            
            # If OverallData is a JSON string, parse it
            if isinstance(overall_data_json, str):
                overall_data = json.loads(overall_data_json)
            else:
                overall_data = overall_data_json
            
            # Extract specific fields from overall_data
            last_update_time = overall_data.get('LastUpdateTime')
            # Perform any additional processing here
            
            # For demonstration, print the extracted data
            # print(f'Row ID: {row_id}')
            
    except Exception as e:
        print(f'Error processing data: {e}')

def print_messages_per_minute():
    global messages_received_in_current_minute
    while True:
        time.sleep(60)  # Wait for one minute
        with lock:
            print(f"Messages received in the last minute: {messages_received_in_current_minute}")
            messages_received_in_current_minute = 0  # Reset the counter for the next minute

def connect_with_retry():
    """
    Attempt to connect to the server. If the connection fails, retry every 5 seconds.
    """
    while True:
        try:
            print('Attempting to connect to the server...')
            sio.connect('http://localhost:5001')
            print('Connection successful!')
            break  # Exit loop once connected
        except socketio.exceptions.ConnectionError:
            print('Connection failed. Retrying in 5 seconds...')
            time.sleep(5)  # Wait for 5 seconds before retrying

if __name__ == '__main__':
    try:
        # Start the messages per minute printer thread
        threading.Thread(target=print_messages_per_minute, daemon=True).start()
        
        # Attempt to connect to the server with retry
        connect_with_retry()

        # Wait for events
        sio.wait()

    except Exception as e:
        print(f'An error occurred: {e} {data}')
