# DATABASE CONFIGURATION 
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'pegasus',
    'database': 'index_data'
}

db_name = 'index_data'
INSTRUMENT_NAME = 'nifty'                               # FOR EXAMPLE 'nifty', 'banknifty','finnifty'
START_DATE = '2021-04-01'                               #YYYY-MM-DD FOR IMPLIED CALCULATION
END_DATE = '2021-04-06'                                 #YYYY-MM-DD FOR IMPLIED CALCULATION

LOG_FILE_NAME = 'implied.txt'                           #LOG FILE FOR IMPLIED FUTURES CALCULATION
EXPIRY_TABLE_NAME ='expiry_details'                     #TABLE NAME FOR EXPIRY DAYS DETAILS FOR THE INSTRUMENT
STRIKE_DIFFERENCE = 50                                  #STRIKE DIFFERENCE FOR THE UNDERLYING INDEX
START_YEAR = 2021                                       #START YEAR FOR EXPIRY CALCULATION
END_YEAR = 2021                                         #END YEAR FOR EXPIRY CALCULATION






