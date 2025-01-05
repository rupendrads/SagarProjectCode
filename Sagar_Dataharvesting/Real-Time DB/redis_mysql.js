const Redis = require('ioredis');
const mysql = require('mysql2');

// Create a Redis client
const redis = new Redis({
  host: 'localhost', // Redis server host
  port: 6379,        // Redis server port
  // Add other Redis configuration options if necessary
});

// Create a MySQL connection pool
const pool = mysql.createPool({
  host: 'localhost',       // MySQL server host
  user: 'root',            // MySQL username
  password: 'root',        // MySQL password
  database: 'sagar_dataharvesting' // MySQL database name
});

// SQL query to create the 'market_data' table if it doesn't exist
const createTableQuery = `
  CREATE TABLE IF NOT EXISTS market_data (
    Id INT NOT NULL AUTO_INCREMENT,           -- Primary key with auto-increment
    MessageCode INT,                          -- MessageCode: Numeric identifier
    MessageVersion INT,                       -- MessageVersion: Numeric identifier
    ApplicationType INT,                      -- ApplicationType: Numeric type
    TokenID INT,                              -- TokenID: Numeric identifier
    ExchangeSegment INT,                      -- ExchangeSegment: Numeric value
    ExchangeInstrumentID INT,                 -- ExchangeInstrumentID: Numeric identifier
    BookType INT,                             -- BookType: Numeric value
    XMarketType INT,                          -- XMarketType: Numeric value
    LastTradedPrice DECIMAL(15, 2),           -- LastTradedPrice: Price, DECIMAL for precision
    LastTradedQuantity INT,                   -- LastTradedQuantity: Quantity
    LastUpdateTime INT,                       -- LastUpdateTime: UNIX timestamp (INT)
    PercentChange DECIMAL(5, 2),              -- PercentChange: Optional, calculated percentage change
    Close DECIMAL(15, 2),                     -- Close: Optional, last close price
    PRIMARY KEY (Id),                         -- Primary key on the Id column
    INDEX idx_token_id (TokenID)              -- Index on TokenID column for fast searches
  );
`;

const insertMarketData = (data) => {
  const query = `
    INSERT INTO market_data (
      MessageCode, MessageVersion, ApplicationType, TokenID, ExchangeSegment, 
      ExchangeInstrumentID, BookType, XMarketType, LastTradedPrice, 
      LastTradedQuantity, LastUpdateTime, PercentChange, Close
    ) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `;

  const values = [
    data.MessageCode,           // MessageCode
    data.MessageVersion,        // MessageVersion
    data.ApplicationType,       // ApplicationType
    data.TokenID,               // TokenID
    data.ExchangeSegment,       // ExchangeSegment
    data.ExchangeInstrumentID,  // ExchangeInstrumentID
    data.BookType,              // BookType
    data.XMarketType,           // XMarketType
    data.LastTradedPrice,       // LastTradedPrice
    data.LastTradedQuantity,    // LastTradedQuantity
    data.LastUpdateTime,        // LastUpdateTime (timestamp)
    data.PercentChange,         // PercentChange (optional, could be NULL)
    data.Close                  // Close (optional, could be NULL)
  ];

  pool.query(query, values, (err, result) => {
    if (err) {
      console.error('Error inserting data into MySQL:', err);
    } else {
      console.log('Data inserted into MySQL:', result);
    }
  });
};

// Function to fetch and process data from Redis using LRANGE and then delete them
const processQueue = async () => {
  let lastQueueCheckTime = Date.now();
  const queueIdleTimeout = 10000; // Timeout in milliseconds (10 seconds)

  try {
    // Ensure the table exists before processing data
    pool.query(createTableQuery, (err, result) => {
      if (err) {
        console.error('Error creating table:', err);
        process.exit(1); // Exit if table creation fails
      } else {
        console.log('Table `market_data` is ready.');
      }
    });

    while (true) {
      console.log('Checking Redis queue...');
      
      // Fetch all items in the 'market_data' list
      const marketDataList = await redis.lrange('market_data', 0, -1);
      
      if (marketDataList.length > 0) {
        console.log(`Fetched ${marketDataList.length} items from Redis`);

        for (const marketData of marketDataList) {
          try {
            const data = JSON.parse(marketData);
            console.log('Parsed data:', data);
            
            // Insert each data item into MySQL
            insertMarketData(data);
          } catch (parseError) {
            console.error('Error parsing JSON data:', parseError);
          }
        }

        // Once all items are processed, delete them from Redis
        await redis.del('market_data');
        console.log('Deleted all items from Redis list after processing');
        
        // Reset the idle timer since we just fetched and processed data
        lastQueueCheckTime = Date.now();
      } else {
        console.log('Queue is empty, checking if the queue is idle...');
      }

      // Check if the queue has been empty for too long
      if (Date.now() - lastQueueCheckTime > queueIdleTimeout) {
        console.log('Queue has been empty for too long. Stopping the process.');
        process.exit(0); // Explicitly exit the process after stopping
      }

      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for 1 second
    }
  } catch (err) {
    console.error('Error processing Redis queue:', err);
    process.exit(1); // Exit with a non-zero code on error
  }
};

// Start processing the queue
processQueue();