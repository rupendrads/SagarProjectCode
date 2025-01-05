import mysql.connector
import os

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pegasus',
    'database': 'index_data'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM upload_status")
    rows = cursor.fetchall()

    current_files = os.listdir('.')
    matching_ids = []
    for row in rows:
        if row['file_name'] in current_files:
            print(row)
            matching_ids.append(row['id'])

    if matching_ids:
        delete_query = "DELETE FROM upload_status WHERE id IN (%s)"
        cursor.execute(delete_query, (matching_ids,))
        conn.commit()
        print(f"Deleted {cursor.rowcount} rows.")
    else:
        print("No matching files found.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()