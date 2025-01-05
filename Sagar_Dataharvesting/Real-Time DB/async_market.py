import asyncio
import threading
import socketio
import ujson as json  # Using ujson for faster JSON parsing
from queue import Queue, Empty
from helpers import Logger
from datetime import datetime
import time

logger = Logger('socket.txt')
lock = threading.Lock()

class MDSocket_io:
    def __init__(self, token, userID, port, queue, combined_token_names,xts,symbol,
                  reconnection=True, reconnection_attempts=10,
                 reconnection_delay=0.5,reconnection_delay_max=10, randomization_factor=1.5, max_http_buffer_size=1000000
                 ):
        
        # self.sid = socketio.Client(reconnection=reconnection, logger=False, engineio_logger=False)
        self.sid = socketio.Client(reconnection=reconnection, logger=False, engineio_logger=False)

        self.eventlistener = self.sid
        self.queue = queue
        self.reconnection_attempts = reconnection_attempts
        self.reconnection_delay = reconnection_delay
        self.reconnection_delay_max = reconnection_delay_max
        self.randomization_factor = randomization_factor
        self.port = port
        self.userID = userID
        self.token = token
        self.xts = xts
        self.symbol= symbol
        self.xts.subscribe_symbols([self.symbol], self.token)
        self.publishFormat = 'JSON'
        self.broadcastMode = "Full"
        self.headers = {'Content-Type': 'application/json', 'Authorization': token}
        self.connection_url = f'{self.port}/?token={self.token}&userID={self.userID}&publishFormat={self.publishFormat}&broadcastMode={self.broadcastMode}'
        # Set engineio options using socketio.Client properties
        self.sid.eio.ping_timeout = 30
        self.sid.eio.ping_interval = 10
        self.sid.eio.max_http_buffer_size = max_http_buffer_size
        # Set async_mode as needed (default is 'threading')

        self.register_event_handlers()  # Register event handlers in the constructor
        self.data1512_counter = 0  # Counter to track the number of data received
        self.data1501_counter = 0  # Counter to track the number of data received
        # self.symbol=symbol
        self.combined_token_names=combined_token_names,
        # self.sid = socketio.AsyncClient()

        
    async def connect(self):
        threading.Thread(target=self.start_socket_connection).start()
        print('connect')

    def start_socket_connection(self):
        print('start_socket_connection')
        attempt = 0
        while attempt < self.reconnection_attempts:
            if not self.sid.connected:
                try:

                    # Ensure the client is disconnected before connecting
                    if self.sid.eio.state != 'disconnected':
                        self.sid.disconnect()
                    
                    if self.sid.connected:
                        self.sid.disconnect()

                    self.sid.connect(
                        url=self.connection_url,
                        headers=self.headers,
                        transports=['websocket'],
                        namespaces=None,
                        socketio_path='/apimarketdata/socket.io'

                    )
                    self.sid.wait()
                    
                except socketio.exceptions.ConnectionError as e:
                    attempt += 1
                    logger.log(f"Connection attempt {attempt} failed: {e}")
                    time.sleep(min(self.reconnection_delay * (1 + self.randomization_factor), self.reconnection_delay_max))
                except Exception as e:
                    logger.log(f"Unexpected error during connection: {e}")
                    break
            else:
                attempt = 0

    def register_event_handlers(self):
        print('register_event_handlers')
        self.sid.on('connect', self.on_connect)
        self.sid.on('disconnect', self.on_disconnect)
        self.sid.on('error', self.on_error)
        self.sid.on('1501-json-full', self.on_message1501_json_full)
        self.sid.on('1512-json-full', self.on_message1512_json_full)

    async def on_connect(self):
        logger.log(f'Market Data Socket connected successfully! @{datetime.now()}')        
        self.reconnection_delay = 1  # Reset reconnection delay on successful connection

    def on_message1501_json_full(self, data):
        self.data1501_counter += 1  # Increment the counter when data is received 
        #logger.log(f'1512 - Counter : @{self.data1501_counter} Data : @{data}')

    def on_message1512_json_full(self, data):
        self.queue.put(data)
        with lock:
            self.data1512_counter += 1
        #self.last_message_time = datetime.now() 
        #logger.log(f'1512 - Counter: {self.data1512_counter} Data :{data}')
        logger.log(f'Counter: {self.data1512_counter}  Symbol: {self.symbol}')
        self.process_queue_if_needed(self.queue)
               
    def process_queue_if_needed(self,queue):
        if queue.qsize() > 0:           
            #print(queue) 
            from indexfuture import insert_data_queue
            try:
                asyncio.run(insert_data_queue(queue, self.combined_token_names))
            except Exception as e:
                logger.log(f"Error processing queue: {e}")

    async def on_disconnect(self):
        try:
            logger.log(f'Market Data Socket disconnected! @{datetime.now()}')       

            if self.sid.reconnection:
                await self.connect()  
        except Exception as e:            
            logger.log(f'Market Data Socket disconnected! @{datetime.now()}')       

    def on_error(self, data):
        logger.log(f'Market Data Error: {data}')
        #print(f'Market Data Error: {data}')

    def get_emitter(self):
        print(f'get_emitter')
        return self.eventlistener

    def disconnect(self):
        print(f'disconnect')
        try:
            if self.sid.connected:
                self.sid.disconnect()
                logger.log(f'Socket disconnected! @{datetime.now()}') 
        except Exception as e:
            print(f'Disconnection Issue @{datetime.now()}')   
            logger.log(f'Disconnection Issue! @{datetime.now()}') 
    

class MDSocketManager:
    def __init__(self, socket_count, token, userID, port, queue, combined_token_name, xts, symbols):
        print(f'MDSocketManager __init__')
        self.sockets = [
            MDSocket_io(token, userID, port, queue, combined_token_name,xts,symbol)
              for symbol in symbols
        ]
        self.queue = queue

    # async def start_all(self):
    #     print(f'start_all')
    #     for socket_instance in self.sockets:
    #         el = socket_instance.get_emitter()
    #         el.on('connect', socket_instance.on_connect)
    #         el.on('1512-json-full', socket_instance.on_message1512_json_full)
    #         socket_instance.on_message1512_json_full('1512-json-full')
    #         await socket_instance.connect()

    async def start_all(self):
        tasks = []
        for socket_instance in self.sockets:
            el = socket_instance.get_emitter()
            el.on('connect', socket_instance.on_connect)
            el.on('1512-json-full', socket_instance.on_message1512_json_full)
            socket_instance.on_message1512_json_full('1512-json-full')
            tasks.append(socket_instance.connect())
        await asyncio.gather(*tasks)
            
    async def on_connect():
        """Connect from the socket."""
        print('Market Data Socket connected successfully!')
        logger.log('symbols subscribed')
        