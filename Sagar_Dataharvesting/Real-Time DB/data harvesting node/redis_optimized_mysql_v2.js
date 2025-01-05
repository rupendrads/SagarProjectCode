const Redis = require('ioredis');
const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');
const { DateTime } = require('luxon');
const csv = require('csv-parser');
const { execSync } = require('child_process'); // Use execSync for synchronous execution

// Create a Redis client
const redis = new Redis({
  host: 'localhost',
  port: 6379,
});

// Function to fetch the database credentials
async function fetchDbCredentials(env, key) {
  try {
    const pythonScript = path.join(__dirname, '../../../Sagar_common/common_function_redis.py');
    const command = `python ${pythonScript} ${env} ${key}`;

    // Execute the Python script synchronously and capture the result
    const result = execSync(command, { encoding: 'utf8' }).trim();
    
    if (!result) {
      throw new Error('Failed to fetch database configuration from Python script.');
    }

    // Parse the JSON result returned by the Python script
    const dbConfig = JSON.parse(result);
    console.log(`Fetched db config: ${JSON.stringify(dbConfig)}`);
    return dbConfig;
  } catch (error) {
    console.error(`Error fetching db details: ${error.message}`);
    throw error;
  }
}

// Environment and key for fetching the database config
const env = "dev";  // Example: 'dev', 'prod'
const key = "db_sagar_dataharvesting";  // Example key for fetching the db configuration

// Load NFO Data Map
let nfoDataMap = null;

// Function to read the CSV file and convert it to a Map for O(1) lookups
const loadNfoData = async () => {
  console.log('Loading NFO data...');
  if (nfoDataMap) {
    return nfoDataMap;
  }

  const result = new Map();
  
  // Resolve the absolute path to the nfo.csv file
  const filePath = path.resolve(__dirname, 'nfo.csv');
  if (!fs.existsSync(filePath)) {
    throw new Error(`nfo.csv file not found at path: ${filePath}`);
  }

  return new Promise((resolve, reject) => {
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        result.set(row['ExchangeInstrumentID'], row['Description']);
      })
      .on('end', () => {
        nfoDataMap = result;
        console.log('CSV file successfully processed into a Map');
        resolve(result);
      })
      .on('error', (err) => {
        reject('Error reading CSV file: ' + err);
      });
  });
};

// Function to load the config file
const loadConfig = (filePath) => {
  return new Promise((resolve, reject) => {
    fs.readFile(filePath, 'utf8', (err, data) => {
      if (err) {
        reject('Error loading config file: ' + err);
      } else {
        resolve(JSON.parse(data));
      }
    });
  });
};

// Function to process and insert data
const processQueue = async (db_creds) => {
  const script = `
    local result = redis.call('LRANGE', KEYS[1], 0, ARGV[1] - 1)
    if #result > 0 then
      redis.call('LTRIM', KEYS[1], ARGV[1], -1)
    end
    return result
  `;

  try {
    const config = await loadConfig('redis_config.json');
    const timezone = config["timezone"].toLowerCase();
    const timeDifference = timezone === "uk" ? 60 : 330; // Time difference in minutes

    const getFormattedDate = () => {
      const today = new Date();
      const year = today.getFullYear();
      const month = (today.getMonth() + 1).toString().padStart(2, '0');
      const day = today.getDate().toString().padStart(2, '0');
      return `${year}${month}${day}`;
    };

    const tableName = `data_harvesting_${getFormattedDate()}`;

    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS \`${tableName}\` (
        Id INT NOT NULL AUTO_INCREMENT,
        MessageCode INT,
        MessageVersion INT,
        ApplicationType INT,
        TokenID INT,
        ExchangeSegment INT,
        ExchangeInstrumentID BIGINT,
        BookType INT,
        XMarketType INT,
        LastTradedPrice DOUBLE,
        LastTradedQuantity INT,
        LastUpdateTime DATETIME,
        PercentChange DOUBLE,
        Close DECIMAL(15, 2),
        Tradingsymbol VARCHAR(255),
        InsertionTime DATETIME DEFAULT CURRENT_TIMESTAMP,
        OverallData JSON,
        PRIMARY KEY (Id),
        KEY idx_ExchangeInstrumentID (ExchangeInstrumentID),
        KEY idx_LastUpdateTime (LastUpdateTime),
        KEY idx_LastTradedPrice (LastTradedPrice)
      );
  `;
  

    const pool = mysql.createPool({
      host: db_creds.host,
      user: db_creds.user,
      password: db_creds.password,
      database: db_creds.database,
      waitForConnections: true,
      connectionLimit: 100,
      queueLimit: 0
    });

    await pool.query(createTableQuery);
    console.log(`Table \`${tableName}\` is ready.`);

    while (true) {
      const listLength = await redis.llen('market_data'); // Get the length of the list
      if (listLength === 0) {
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Wait for 1 second if the list is empty
        continue;
      }

      const batchSize = listLength; 
      const dataList = await redis.eval(script, 1, 'market_data', batchSize); // Fetch and trim the data
      console.log(`Fetched ${dataList.length} items from Redis`);

      const processedDataBatch = dataList.map((item) => {
        let marketData;
        try {
          marketData = JSON.parse(item);
        } catch (parseError) {
          console.error('Error parsing JSON data:', parseError);
          return null;
        }

        const adjustedLastUpdateTime = marketData.LastUpdateTime !== null
          ? DateTime.fromSeconds(marketData.LastUpdateTime)
              .minus({ days: 1 }) 
              .minus({ minutes: timeDifference }) 
              .toFormat('yyyy-LL-dd HH:mm:ss')
          : null;

        const overallData = JSON.stringify(marketData);
        const tradingSymbol = nfoDataMap.get(marketData.ExchangeInstrumentID.toString()) || null;

        return [
          marketData.MessageCode,
          marketData.MessageVersion,
          marketData.ApplicationType,
          marketData.TokenID,
          marketData.ExchangeSegment,
          marketData.ExchangeInstrumentID,
          marketData.BookType,
          marketData.XMarketType,
          marketData.LastTradedPrice,
          marketData.LastTradedQunatity,
          adjustedLastUpdateTime,
          marketData.PercentChange,
          marketData.Close,
          tradingSymbol,
          overallData
        ];
      }).filter(item => item !== null);

      await insertMarketDataBatch(processedDataBatch, tableName, pool);
    }
  } catch (err) {
    console.error('Error processing Redis queue:', err);
  }
};

const insertMarketDataBatch = async (dataBatch, tableName, pool) => {
  if (dataBatch.length === 0) return;

  const placeholders = dataBatch.map(() => '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)').join(', ');
  const values = [];
  for (const data of dataBatch) {
    values.push(...data);
  }

  const query = `
    INSERT INTO \`${tableName}\` (
      MessageCode, MessageVersion, ApplicationType, TokenID, ExchangeSegment,
      ExchangeInstrumentID, BookType, XMarketType, LastTradedPrice,
      LastTradedQuantity, LastUpdateTime, PercentChange, Close, Tradingsymbol, OverallData
    ) VALUES ${placeholders}
  `;

  try {
    await pool.query(query, values);
    console.log(`Inserted ${dataBatch.length} records into MySQL table: ${tableName}`);
  } catch (err) {
    console.error('Error inserting data into MySQL:', err);
  }
};

// Function to execute the NFO generator script and wait for its completion
const runNfoGenerator = () => {
  return new Promise((resolve, reject) => {
    try {
      console.log('Running NFO Generator...');
      // Using execSync for synchronous execution, it will block until completion
      execSync('node nfo_generator.js', { stdio: 'inherit' }); // `stdio: 'inherit'` will show the output in the console
      console.log('NFO Generator has completed.');
      resolve();
    } catch (err) {
      reject(`Error running NFO Generator: ${err.message}`);
    }
  });
};

// Run the NFO Generator, then load CSV and process queue
(async () => {
  try {
    // Fetch db credentials dynamically
    const db_creds = await fetchDbCredentials(env, key);

    // Run NFO Generator script synchronously, wait for it to finish
    await runNfoGenerator();

    // Load NFO data after the generator has completed
    await loadNfoData();

    // Start processing the Redis queue with the fetched db credentials
    await processQueue(db_creds);
  } catch (err) {
    console.error('Error during initialization:', err);
  }
})();
