const Redis = require('ioredis');
const mysql = require('mysql2');
const fs = require('fs');
const { DateTime } = require('luxon'); // Luxon for date-time manipulation
const csv = require('csv-parser');
const path = require('path');

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

// Global object to store the NFO data
let nfoData = null;

// Function to read the CSV file and convert it to a dictionary
const loadNfoData = async () => {
  if (nfoData) {
    // If data is already loaded, return it immediately
    return nfoData;
  }

  const result = {
    ExchangeInstrumentID: [],
    Description: []
  };

  return new Promise((resolve, reject) => {
    fs.createReadStream('nfo.csv')
      .pipe(csv())
      .on('data', (row) => {
        // Push the values into the respective arrays
        result.ExchangeInstrumentID.push(row['ExchangeInstrumentID']);
        result.Description.push(row['Description']);
      })
      .on('end', () => {
        // Store the loaded data in the global variable
        nfoData = result;
        console.log('CSV file successfully processed');
        resolve(result);
      })
      .on('error', (err) => {
        reject('Error reading CSV file: ' + err);
      });
  });
};

// Call the loadNfoData function once when the app starts
(async () => {
  await loadNfoData(); // This will load the CSV data into memory
})();


// Function to load the config file
const loadConfig = (filePath) => {
  return new Promise((resolve, reject) => {
    fs.readFile(filePath, 'utf8', (err, data) => {
      if (err) {
        reject('Error loading config file:', err);
      } else {
        resolve(JSON.parse(data));
      }
    });
  });
};

// Function to fetch and process data from Redis using LRANGE and then delete them
const processQueue = async () => {
  let lastQueueCheckTime = Date.now();
  const queueIdleTimeout = 60000; // Timeout in milliseconds (60 seconds)
  const dataQueue = []; // This will hold the data temporarily

  // Get the current date in YYYYMMDD format
  const getFormattedDate = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = (today.getMonth() + 1).toString().padStart(2, '0'); // Ensure 2 digits for month
    const day = today.getDate().toString().padStart(2, '0'); // Ensure 2 digits for day
    return `${year}${month}${day}`;
  };

  const tableName = `data_harvesting_${getFormattedDate()}`;

  // SQL query to create the dynamic table
  const createTableQuery = `
    CREATE TABLE IF NOT EXISTS \`${tableName}\` (
      Id INT NOT NULL AUTO_INCREMENT,           -- Primary key with auto-increment
      MessageCode INT,                          -- MessageCode: Numeric identifier
      MessageVersion INT,                       -- MessageVersion: Numeric identifier
      ApplicationType INT,                      -- ApplicationType: Numeric type
      TokenID INT,                              -- TokenID: Numeric identifier
      ExchangeSegment INT,                      -- ExchangeSegment: Numeric value
      ExchangeInstrumentID INT,                 -- ExchangeInstrumentID: Numeric identifier
      BookType INT,                             -- BookType: Numeric value
      XMarketType INT,                          -- XMarketType: Numeric value
      LastTradedPrice FLOAT,           -- LastTradedPrice: Price, DECIMAL for precision
      LastTradedQuantity INT,                   -- LastTradedQuantity: Quantity
      LastUpdateTime DATETIME,                       -- LastUpdateTime: UNIX timestamp (INT)
      PercentChange DECIMAL(5, 2),              -- PercentChange: Optional, calculated percentage change
      Close DECIMAL(15, 2), 
      Tradingsymbol VARCHAR(255),    
      InsertionTime DATETIME DEFAULT CURRENT_TIMESTAMP,               -- Close: Optional, last close price
      OverallData TEXT,                    
      PRIMARY KEY (Id)                          -- Primary key on the Id column
    );
  `;

  try {
    // Create the table dynamically before starting to process any data
    await new Promise((resolve, reject) => {
      pool.query(createTableQuery, (err, result) => {
        if (err) {
          reject('Error creating table: ' + err);
        } else {
          console.log(`Table \`${tableName}\` is ready.`);
          resolve();
        }
      });
    });

    while (true) {
      console.log('Checking Redis queue...');

      // Fetch new items from the 'market_data' list in Redis
      const marketDataList = await redis.lrange('market_data', 0, -1);
      
      if (marketDataList.length > 0) {
        console.log(`Fetched ${marketDataList.length} items from Redis`);

        // Add the new items to the dataQueue
        marketDataList.forEach((item) => {
          try {
            const data = JSON.parse(item);
            console.log('Parsed data:', data);
            dataQueue.push(data); // Store the data in the queue
          } catch (parseError) {
            console.error('Error parsing JSON data:', parseError);
          }
        });
        
        // Reset the idle timer since we just fetched new data
        lastQueueCheckTime = Date.now();
      } else {
        console.log('Queue is empty, checking if the queue is idle...');
      }

      // Process the queue if there are any items
      if (dataQueue.length > 0) {
        console.log(`Processing ${dataQueue.length} items in the queue...`);
        while (dataQueue.length > 0) {
          const marketData = dataQueue.shift(); // Get and remove the first item in the queue
          try {
            // Insert each data item into MySQL with dynamic table name
            await insertMarketData(marketData, tableName);
      
            // Use ltrim to remove the first item (index 0) from the Redis list
            await redis.ltrim('market_data', 1, -1);
            console.log('Trimmed Redis list, removed the first item.');
      
          } catch (insertError) {
            console.error('Error inserting data into MySQL:', insertError);
          }
        }
      }

      // Check if the queue has been empty for too long
      if (Date.now() - lastQueueCheckTime > queueIdleTimeout) {
        console.log('Queue has been empty for too long. Stopping the process.');
        process.exit(0); // Explicitly exit the process after stopping
      }

      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for 1 second before checking again
    }
  } catch (err) {
    console.error('Error processing Redis queue:', err);
    process.exit(1); // Exit with a non-zero code on error
  }
};

// Modified insert function to use dynamic table name and adjust LastUpdateTime
const insertMarketData = async (data, tableName) => {
  let time_difference = 0;

  // Load configuration for timezone and calculate time difference
  const config = await loadConfig('redis_config.json');
  if (config["timezone"].toLowerCase() === "uk") {
    time_difference = 60; // UK timezone, 60 minutes difference
  } else {
    time_difference = 330; // Other timezones, 330 minutes difference (likely for IST)
  }

  // Adjust LastUpdateTime based on the time difference
  const adjustedLastUpdateTime = data.LastUpdateTime !== null 
    ? DateTime.fromSeconds(data.LastUpdateTime) // Convert the timestamp to DateTime
        .minus({ minutes: time_difference }) // Adjust for timezone (if needed)
        .toFormat('yyyy-LL-dd HH:mm:ss') // Format as MySQL DATETIME format
    : null;
  const overallData = JSON.stringify(data);
  
  // Load the mapping data from the CSV (nfoData should already be loaded)
  const nfo = await loadNfoData();

  // Check if the ExchangeInstrumentID exists in the nfoData and get the Description
  const descriptionIndex = nfo.ExchangeInstrumentID.indexOf(data.ExchangeInstrumentID.toString());
  const tradingIndex = descriptionIndex !== -1 ? nfo.Description[descriptionIndex] : null;

  const query = `
    INSERT INTO \`${tableName}\` (
      MessageCode, MessageVersion, ApplicationType, TokenID, ExchangeSegment, 
      ExchangeInstrumentID, BookType, XMarketType, LastTradedPrice, 
      LastTradedQuantity, LastUpdateTime, PercentChange, Close, Tradingsymbol, OverallData
    ) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    data.LastTradedQunatity,    // LastTradedQuantity
    adjustedLastUpdateTime,     // Adjusted LastUpdateTime (using the new logic)
    data.PercentChange,         // PercentChange (optional, could be NULL)
    data.Close,
    tradingIndex,
    overallData                 // Close (optional, could be NULL)
  ];

  await new Promise((resolve, reject) => {
    pool.query(query, values, (err, result) => {
      if (err) {
        reject('Error inserting data into MySQL: ' + err);
      } else {
        console.log('Data inserted into MySQL table:', tableName);
        resolve(result);
      }
    });
  });
};

// Start processing the queue
processQueue();
