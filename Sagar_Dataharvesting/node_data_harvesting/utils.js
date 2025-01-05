const mysql = require('mysql2/promise');
const moment = require('moment');
const config = require('./config.json');

async function createDatabaseAndTable() {
  try {
    const connection = await mysql.createConnection({
      host: config.database.host,
      user: config.database.user,
      password: config.database.password,
    });

    // Create the database if it doesn't exist
    await connection.query(`CREATE DATABASE IF NOT EXISTS ${config.database.database}`);

    // Switch to the created database
    await connection.changeUser({ database: config.database.database });

    const tableName = `data_${moment().format("YYYY-MM-DD")}_node`;
    const tableExists = await connection.query(`SHOW TABLES LIKE '${tableName}'`);
    if (tableExists[0].length === 0) {
      await connection.query(`
        CREATE TABLE \`${tableName}\` (
          id INT AUTO_INCREMENT PRIMARY KEY,
          data VARCHAR(255)
        )
      `);
      console.log(`Created table ${tableName}`);
    }

    await connection.end();
  } catch (error) {
    console.error('Error creating database or table:', error);
  }
}

async function insertDataIntoTable(data) {
  try {
    const connection = await mysql.createConnection({
      host: config.database.host,
      user: config.database.user,
      password: config.database.password,
      database: config.database.database,
    });

    const tableName = `data_${moment().format("YYYY-MM-DD")}_node`;
    
    await connection.query(`
      INSERT INTO \`${tableName}\` (data) VALUES (?)
    `, [JSON.stringify(data)]);

    await connection.end();
  } catch (error) {
    console.error('Error inserting data:', error);
  }
}

module.exports = {
  createDatabaseAndTable,
  insertDataIntoTable,
};

createDatabaseAndTable()