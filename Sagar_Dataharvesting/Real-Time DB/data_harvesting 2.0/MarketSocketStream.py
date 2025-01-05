import threading
import socketio
import json
from datetime import datetime
from utils import Logger
import time
import redis

logger = Logger('socket_log.txt')

class MDSocket_io:
    def __init__(self, token, userID, port, publisher, reconnection=True, reconnection_attempts=0, reconnection_delay=1,
                 reconnection_delay_max=50000, randomization_factor=0.5, logger=False, binary=False, json=None,
                 **kwargs):
        self.publisher = publisher
        self.sid = socketio.Client(logger=False, engineio_logger=False)
        self.eventlistener = self.sid
        self.market_socket_data = []
        self.received_message_count = 0
        self.register_event_handlers()
        self.reconnection_delay = reconnection_delay
        self.randomization_factor = randomization_factor
        self.reconnection_delay_max = reconnection_delay_max
        self.port = port
        self.userID = userID
        self.token = token
        self.publishFormat = 'JSON'
        self.broadcastMode = "Full"
        self.headers = {'Content-Type': 'application/json', 'Authorization': token}
        self.connection_url = f'{self.port}/?token={self.token}&userID={self.userID}&publishFormat={self.publishFormat}&broadcastMode={self.broadcastMode}'
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.redis_message_count_key = 'market_data_count'
        self.namespaces_lock = threading.Lock()
    def connect(self):
        threading.Thread(target=self.start_socket_connection).start()

    def start_socket_connection(self):
        while True:
            if not self.sid.connected:
                try:
                    try:
                        self.sid.connect(
                            url=self.connection_url,
                            headers=self.headers,
                            transports='websocket',
                            namespaces=None,
                            socketio_path='/apimarketdata/socket.io'
                        )
                        self.sid.wait()
                    except:
                        print("already connected")
                except socketio.exceptions.ConnectionError as e:
                    pass
            else:
                pass

    def register_event_handlers(self):
        self.sid.on('connect', self.on_connect)
        self.sid.on('disconnect', self.on_disconnect)
        self.sid.on('error', self.on_error)
        self.sid.on('1501-json-full', self.on_message1501_json_full)
        self.sid.on('1512-json-full', self.on_message1512_json_full)
        self.sid.on('disconnect', self.on_disconnect)
        self.sid.on('error', self.on_error)

    def on_connect(self):
        print('Market Data Socket connected successfully!')
        logger.log(f'socket reconnected @ {datetime.now()}')

    def on_message1501_json_full(self, data):
        print('I received a 1501 Level1, Touchline message!', data)

    def on_message1512_json_full(self, data):
        self.received_message_count += 1
        data = json.loads(data)
        # print(data)
        self.redis_client.rpush('market_data', json.dumps(data))
        self.redis_client.incr(self.redis_message_count_key)

    def verify_message_counts(self):
        redis_message_count = int(self.redis_client.get(self.redis_message_count_key) or 0)
        if self.received_message_count == redis_message_count:
            print(f"All messages are successfully saved to Redis! Count: {self.received_message_count}")
        else:
            print(f"Data mismatch! Received: {self.received_message_count}, Saved in Redis: {redis_message_count}")

    def on_disconnect(self):
        with self.namespaces_lock:
            try:
                print('Market Data Socket disconnected!')
                logger.log(f'socket disconnected @ {datetime.now()}')
            except RuntimeError as e:
                print(f"Disconnect handler error: {e}")

    def on_error(self, data):
        print('Market Data Error:', data)

    def get_emitter(self):
        return self.eventlistener

    def disconnect(self):
        self.sid.disconnect()
