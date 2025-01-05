import mysql.connector

from constants import db_credentials
db_credentials.pop('database', None)


create_database_query = "CREATE DATABASE IF NOT EXISTS sagar_strategy;"
use_database_query = "USE sagar_strategy;"
create_table_optimisation_query = """
CREATE TABLE IF NOT EXISTS `optimisation` (
  `op_id` int NOT NULL AUTO_INCREMENT,
  `strategy_id` int DEFAULT NULL,
  `optimization_key` varchar(255) DEFAULT NULL,
  `full_json` json DEFAULT NULL,
  PRIMARY KEY (`op_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""
create_table_optimisation_details_query = """
CREATE TABLE IF NOT EXISTS `optimisation_details` (
  `id` int NOT NULL AUTO_INCREMENT,
  `op_id` int DEFAULT NULL,
  `combination_parameter` json DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `response_result` json DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `user` varchar(255) DEFAULT NULL,
  `sequence_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `op_id` (`op_id`),
  CONSTRAINT `optimisation_details_ibfk_1` FOREIGN KEY (`op_id`) REFERENCES `optimisation` (`op_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

# Connecting to MySQL server and executing queries
try:
    # Connect to the MySQL server
    connection = mysql.connector.connect(**db_credentials)
    cursor = connection.cursor()

    # Create database
    cursor.execute(create_database_query)
    print("Database created successfully (if it didn't exist).")

    # Select the database
    cursor.execute(use_database_query)
    print("Database switched successfully.")

    # Create tables
    cursor.execute(create_table_optimisation_query)
    print("Table 'optimisation' created successfully (if it didn't exist).")

    cursor.execute(create_table_optimisation_details_query)
    print("Table 'optimisation_details' created successfully (if it didn't exist).")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    # Close the connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Connection closed.")

