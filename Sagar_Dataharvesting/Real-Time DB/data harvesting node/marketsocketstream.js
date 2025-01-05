const socketio = require('socket.io-client');
const { createClient } = require('redis');
const fs = require('fs');

class MDSocket_io {
    constructor(token, userID, port, {
        reconnection = true,
        reconnectionAttempts = 0,
        reconnectionDelay = 1,
        reconnectionDelayMax = 50000,
        randomizationFactor = 0.5,
        logger = false,
        binary = false,
        json = null
    } = {}) {
        // Socket.IO client initialization
        this.sid = socketio;
        this.eventListener = this.sid;
        this.marketSocketData = [];
        this.receivedMessageCount = 0;
        
        // Connection parameters
        this.reconnectionDelay = reconnectionDelay;
        this.randomizationFactor = randomizationFactor;
        this.reconnectionDelayMax = reconnectionDelayMax;
        this.port = port;
        this.userID = userID;
        this.token = token;
        this.publishFormat = 'JSON';
        this.broadcastMode = 'Full';
        
        // Connection URL and headers
        this.headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        };
        this.connectionUrl = `${this.port}/?token=${this.token}&userID=${this.userID}&publishFormat=${this.publishFormat}&broadcastMode=${this.broadcastMode}`;
        
        // Redis initialization
        this.redisClient = createClient({
            host: 'localhost',
            port: 6379,
            db: 0
        });
        this.redisMessageCountKey = 'market_data_count';
        
        // Initialize Redis connection
        this.initRedis();
    }

    async initRedis() {
        try {
            await this.redisClient.connect();
            console.log('Connected to Redis');
        } catch (err) {
            console.error('Failed to connect to Redis:', err);
        }
    }

    connect() {
        // Start connection in a non-blocking way
        setTimeout(() => this.startSocketConnection(), 0);
    }

    // startSocketConnection() {
    //     const attemptConnection = () => {
    //         if (!this.socket || !this.socket.connected) {
    //             try {
    //                 console.log('Attempting to connect to market data socket...');
    //                 this.socket = this.sid.connect(this.connectionUrl, {
    //                     headers: this.headers,
    //                     transports: ['websocket'],
    //                     path: '/apimarketdata/socket.io',
    //                     reconnection: true,
    //                     reconnectionAttempts: Infinity,
    //                     reconnectionDelay: this.reconnectionDelay,
    //                     reconnectionDelayMax: this.reconnectionDelayMax,
    //                     randomizationFactor: this.randomizationFactor
    //                 });

    //                 this.registerEventHandlers();
    //             } catch (error) {
    //                 console.error('Connection error:', error);
    //                 setTimeout(attemptConnection, 5000); // Retry after 5 seconds
    //             }
    //         }
    //     };

    //     attemptConnection();
    // }
    startSocketConnection() {
        const attemptConnection = () => {
            if (!this.socket || !this.socket.connected) {
                try {
                    console.log('Detailed Connection Parameters:');
                    console.log('Full URL:', this.connectionUrl);
                    console.log('Token:', this.token);
                    console.log('User ID:', this.userID);
                    console.log('Publish Format:', this.publishFormat);
                    console.log('Broadcast Mode:', this.broadcastMode);
    
                    // More comprehensive connection configuration
                    this.socket = this.sid.connect(this.port, {
                        reconnection: true,
                        reconnectionAttempts: Infinity,
                        reconnectionDelay: this.reconnectionDelay,
                        reconnectionDelayMax: this.reconnectionDelayMax,
                        randomizationFactor: this.randomizationFactor,
                        transports: ['websocket'],
                        timeout: 10000,
                        forceNew: true,
                        path: '/apimarketdata/socket.io', // Specific path if required
                        query: {
                            token: this.token,
                            userID: this.userID,
                            publishFormat: this.publishFormat,
                            broadcastMode: this.broadcastMode
                        },
                        extraHeaders: {
                            'Authorization': this.token,
                            'Content-Type': 'application/json'
                        }
                    });
    
                    // Comprehensive event logging
                    this.socket.on('connect', () => {
                        console.log('Socket Connected Successfully');
                        console.log('Socket ID:', this.socket.id);
                    });
    
                    this.socket.on('disconnect', (reason) => {
                        console.log('Socket Disconnected. Reason:', reason);
                    });
    
                    this.socket.on('connect_error', (error) => {
                        console.error('Connection Error Details:', {
                            name: error.name,
                            message: error.message,
                            stack: error.stack
                        });
                    });
    
                    this.socket.on('reconnect_attempt', (attemptNumber) => {
                        console.log(`Attempting to reconnect. Attempt: ${attemptNumber}`);
                    });
    
                    this.registerEventHandlers();
                } catch (error) {
                    console.error('Socket Connection Initialization Catastrophic Error:', error);
                    setTimeout(attemptConnection, 5000);
                }
            }
        };
    
        attemptConnection();
    }
    registerEventHandlers() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
            console.log('Market Data Socket connected successfully!');
            console.log(`socket reconnected @ ${new Date().toISOString()}`);
        });

        this.socket.on('1501-json-full', (data) => {
            console.log('Received 1501 Level1, Touchline message!', data);
        });

        this.socket.on('1512-json-full', async (data) => {
            // console.log('Received 1512 Level2, Touchline message!', data);
            this.receivedMessageCount += 1;
            const jsonData = typeof data === 'string' ? JSON.parse(data) : data;
            try {
                await this.redisClient.rPush('market_data', JSON.stringify(jsonData));
                await this.redisClient.set(this.redisMessageCountKey, this.receivedMessageCount);
                
                // Log the receivedMessageCount to datacounter.txt
                fs.writeFile('datacounter.txt', `Received Message Count: ${this.receivedMessageCount}`, (err) => {
                    if (err) {
                        console.error('Error writing to datacounter.txt:', err);
                    }
                });
            } catch (err) {
                console.error('Error saving to Redis:', err);
            }
        });

        this.socket.on('disconnect', () => {
            console.log('Market Data Socket disconnected!');
            console.log(`socket disconnected @ ${new Date().toISOString()}`);
        });

        this.socket.on('error', (data) => {
            console.log('Market Data Error:', data);
        });
    }

    async verifyMessageCounts() {
        try {
            const redisMessageCount = parseInt(await this.redisClient.get(this.redisMessageCountKey)) || 0;
            if (this.receivedMessageCount === redisMessageCount) {
                console.log(`All messages are successfully saved to Redis! Count: ${this.receivedMessageCount}`);
            } else {
                console.log(`Data mismatch! Received: ${this.receivedMessageCount}, Saved in Redis: ${redisMessageCount}`);
            }
        } catch (err) {
            console.error('Error verifying message counts:', err);
        }
    }

    getEmitter() {
        return this.eventListener;
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
        this.redisClient.quit();
    }
}

module.exports = MDSocket_io;