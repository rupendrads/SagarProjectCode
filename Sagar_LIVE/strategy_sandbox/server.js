require('dotenv').config();
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');

// Constants and configurations
const PORT = 5001;
const {
  host,
  user,
  password,
  database,
  table_name: TABLE_NAME,
  MODE,
  DATA_PER_MINUTE
} = require('./constants');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, { cors: { origin: "*" } });
const LAST_ID_FILE = path.join(__dirname, 'last_id.txt');

// Database pool configuration
const pool = mysql.createPool({
  host,
  user,
  password,
  database,
  waitForConnections: true,
  connectionLimit: 5,
  queueLimit: 0,
  charset: 'utf8mb4'
});

// Function to read the last processed ID
const readLastId = () => fs.existsSync(LAST_ID_FILE) ? parseInt(fs.readFileSync(LAST_ID_FILE, 'utf-8')) : 0;

// Function to write the last processed ID
const writeLastId = (lastId) => fs.writeFileSync(LAST_ID_FILE, String(lastId));

// Handle Socket.io connection
io.on('connection', (socket) => {
  console.log('Client connected');
  socket.emit('message', { data: 'Connected to server' });

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

// Function to convert UNIX timestamp to GMT date
const convertToGMT = (timestamp) => new Date(timestamp * 1000).toISOString();

// Fetch and push data based on `database_time` mode
const pushDataInRealTime = async () => {
  let lastId = readLastId();

  while (true) {
    try {
      const conn = await pool.getConnection();
      const [rows] = await conn.query(
        `SELECT id, OverallData FROM ${TABLE_NAME} WHERE id > ? ORDER BY JSON_EXTRACT(OverallData, "$.LastUpdateTime") ASC`, [lastId]
      );
      conn.release();

      let i = 0;
      while (i < rows.length) {
        const batch = [];
        const row = rows[i];
        const currentOverallData = JSON.parse(row.OverallData);
        const currentLastUpdateTime = currentOverallData.LastUpdateTime;

        // Collect all rows with the same LastUpdateTime
        while (i < rows.length) {
          const row = rows[i];
          const overallData = JSON.parse(row.OverallData);
          if (overallData.LastUpdateTime === currentLastUpdateTime) {
            batch.push({
              id: row.id,
              OverallData: overallData
            });
            i++;
          } else {
            break;
          }
        }

        // Emit the batch
        io.emit('message', { data: batch });
        console.log(`Data batch sent at ${convertToGMT(currentLastUpdateTime)} GMT:`, batch);

        // Update lastId after processing the batch
        writeLastId(batch[batch.length - 1].id);
        lastId = batch[batch.length - 1].id;

        // Calculate time difference to the next batch
        if (i < rows.length) {
          const nextOverallData = JSON.parse(rows[i].OverallData);
          const nextLastUpdateTime = nextOverallData.LastUpdateTime;
          const timeDifference = (nextLastUpdateTime - currentLastUpdateTime) * 1000;

          // Wait for the time difference
          await new Promise(resolve => setTimeout(resolve, timeDifference));
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
};

// Fetch and push data based on `data_per_minute` mode
const pushDataPerMinute = async (dataPerMinute) => {
  let lastId = readLastId();
  const intervalPerData = (60 * 1000) / dataPerMinute;

  while (true) {
    try {
      const conn = await pool.getConnection();
      const [rows] = await conn.query(
        `SELECT id, OverallData FROM ${TABLE_NAME} WHERE id > ? ORDER BY id ASC`, [lastId]
      );
      conn.release();

      for (const row of rows) {
        const overallData = JSON.parse(row.OverallData);
        const lastUpdateTime = convertToGMT(overallData.LastUpdateTime);

        io.emit('message', { data: row });
        console.log(`Data sent at ${lastUpdateTime} GMT:`, row);
        writeLastId(row.id);
        lastId = row.id;

        await new Promise(resolve => setTimeout(resolve, intervalPerData));  // Wait based on the interval
      }
    } catch (error) {
      console.error('Error polling database:', error);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
};

// Start the server based on the selected mode
server.listen(PORT, () => {
  console.log(`Socket.IO server running at http://localhost:${PORT}/`);
  console.log(`Mode selected: ${MODE}`);
  
  if (MODE === 'database_time') {
    pushDataInRealTime();
  } else if (MODE === 'data_per_minute') {
    pushDataPerMinute(DATA_PER_MINUTE);
  } else {
    console.error('Invalid MODE selected. Choose either "database_time" or "data_per_minute".');
  }
});
