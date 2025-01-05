import os
import importlib
from sqlalchemy import create_engine, Column, Date, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from db_config import db_config

def get_db_config():
    return {
        'host': db_config['DB_HOST'],
        'database': db_config['DB_NAME'],
        'user': db_config['DB_USER'],
        'password': db_config['DB_PASSWORD']
    }

def create_db_session():
    config = get_db_config()
    connection_string = f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
    engine = create_engine(connection_string, echo=True)
    Session = sessionmaker(bind=engine)
    return engine, Session()

def create_trading_days_table(engine):
    metadata = MetaData()
    trading_days_table = Table(
        'trading_days', metadata,
        Column('trading_day', Date, primary_key=True)
    )
    metadata.create_all(engine)
    return trading_days_table

def insert_trading_days_from_files(session, trading_days_table):
    trading_days_dir = './'  

    for file_name in os.listdir(trading_days_dir):
        if file_name.startswith('trading_days_') and file_name.endswith('.py'):
            module_name = file_name.replace('.py', '')
            module = importlib.import_module(module_name)
            trading_days_list = getattr(module, module_name)
            
            for trading_day in trading_days_list:
                try:
                    session.execute(trading_days_table.insert().values(trading_day=trading_day))
                except IntegrityError:
                    session.rollback()  
                else:
                    session.commit()

def main():
    engine, session = create_db_session()
    trading_days_table = create_trading_days_table(engine)
    insert_trading_days_from_files(session, trading_days_table)
    print("Trading days have been successfully uploaded to the database.")

if __name__ == "__main__":
    main()
