from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
)
import sys
import json

def process_binlog():
    stream = BinLogStreamReader(
        connection_settings={
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "passwd": "root",
            "database": "sagar_dataharvesting" 
        },
        only_tables=["data_harvesting_20240611"], 
        only_events=[WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent],
        server_id=100,
        blocking=True
    )

    for binlogevent in stream:
        for row in binlogevent.rows:
            # event = {"schema": binlogevent.schema, "table": binlogevent.table}
            # if isinstance(binlogevent, WriteRowsEvent):
            #     event["action"] = "insert"
            #     event["data"] = row           
            print(row)

    stream.close()

if __name__ == "__main__":
    process_binlog()
