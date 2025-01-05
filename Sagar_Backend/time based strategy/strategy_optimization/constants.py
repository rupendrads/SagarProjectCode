# LOT SIZE
BANKNIFTY_LOT_SIZE = 15
NIFTY_LOT_SIZE = 25
FINNIFTY_LOT_SIZE = 25
MIDCAPNIFTY_LOT_SIZE = 75
SENSEX_LOT_SIZE = 10

VALID_INDICES =[]

#STRIKE DIFFERENCE i.e. base values used for determining ATM
BANKNIFTY_BASE = 100
NIFTY_BASE = 50
FINNIFTY_BASE = 50
MIDCAPNIFTY_BASE = 100
SENSEX_BASE = 100


#TIME FORMAT PASSED FOR START_TIME, EXIT_TIME, LAST_ENTRY_TIME
TIMEFORMAT = "%H:%M:%S"


charges = {
    'exchangeTransactionCharge':0.053,
    'stt': 0.05,
    'exchangeTransactionCharge': 0.03503,
    'sebiCharge': 0.000118,
    'stampDuty' : 0.003,
    'ctt': 0.1,
    'brokerage': 20,
    'ipft': 50
}


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pegasus',
    'database': 'index_data',
}


STRATEGY_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pegasus',
    'database': 'sagar_strategy'
}

db_credentials = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pegasus',
    'database' : 'sagar_strategy'
}