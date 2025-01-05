import mysql.connector
import json
import os
import sys

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current script
    sagar_common_path = os.path.join(current_dir, "../../Sagar_common")  # Go up two levels to "OGCODE"
    if sagar_common_path not in sys.path:
        sys.path.append(sagar_common_path)
    from common_function import fetch_parameter
except ImportError as e:
    print(f"Error fetching db details: {e}")

env = "dev"  # Environment, e.g., 'dev', 'prod'
key = "db_sagar_strategy"  # Example key to fetch the database configuration
db_Value = fetch_parameter(env, key)

if db_Value is None:
    raise HTTPException(status_code=500, detail="Failed to fetch database configuration.")

print(f"Fetched db config: {db_Value}")

# Use the fetched database configuration to connect to MySQL
mydb = mysql.connector.connect(
    host=db_Value['host'],
    user=db_Value['user'],
    password=db_Value['password'],
    database=db_Value['database']
)

def convert_to_json(result,strategy_id,value):
    strategies = []
    #print('5')
    mycursor = mydb.cursor()
    #print(result)
    for row in result:
        strategy = {
            "id": row["id"],
            "name": row["name"],
             "underlying":row["underlying"],
             "strategy_type": row["strategy_type"],
             "implied_futures_expiry": row["implied_futures_expiry"],
             "entry_time": row["entry_time"],
             "last_entry_time": row["last_entry_time"],
             "exit_time": row["exit_time"],
             "square_off": row["square_off"],
             "overall_sl": row["overall_sl"],
             "overall_target": row["overall_target"],
              "trailing_options": row["trailing_options"],
              "profit_reaches": row["profit_reaches"],
              "lock_profit": row["lock_profit"],
              "increase_in_profit": row["increase_in_profit"],
              "trail_profit": row["trail_profit"],
              "createdBy" : row["createdBy"],
              "createdDate" : row["createdDate"],
              "modifiedBy" : row["modifiedBy"],
              "lastUpdatedDateTime" : row["lastUpdatedDateTime"],
             "legs": []
            
            }
    
        
    # Fetch data for legs related to the current strategy
        #('6')
        leg_sql = """SELECT id,atm_straddle_premium,closest_premium,leg_no,lots,no_of_reentry,option_type,percent_of_atm_strike_sign,percent_of_atm_strike_value,position,range_breakout,roll_strike,roll_strike_increase_in_profit,roll_strike_lock_profit,roll_strike_lock_profit_sign,
                    roll_strike_profit_reaches,roll_strike_stop_loss,roll_strike_stop_loss_sign,roll_strike_strike_type,roll_strike_trail_profit,roll_strike_trail_profit_sign,roll_strike_trailing_options,
                    simple_momentum,simple_momentum_direction,simple_momentum_range_breakout,simple_momentum_sign,straddle_width_sign,straddle_width_value,strategy_id,strike_selection_criteria,
                    strike_selection_criteria_increase_in_profit,strike_selection_criteria_lock_profit,strike_selection_criteria_lock_profit_sign,strike_selection_criteria_profit_reaches,strike_selection_criteria_stop_loss,
                    strike_selection_criteria_stop_loss_sign,strike_selection_criteria_trail_profit,strike_selection_criteria_trail_profit_sign,strike_selection_criteria_trailing_options,strike_type,expiry,createdBy,createdDate,modifiedBy,lastUpdatedDateTime FROM leg WHERE strategy_id = %s"""  # Replace 'legs' and 'strategy_id' with your table and column names
        mycursor.execute(leg_sql, (strategy_id,))
        leg_rows = mycursor.fetchall()
        #print(leg_rows)
    # Iterate over leg rows and format data into the desired structure
        for leg_row in leg_rows:
            #print('9')
            #print(leg_row)
            leg = {
                "atm_straddle_premium": leg_row[1],
                "closest_premium": leg_row[2],
				"id": leg_row[0],
                "leg_no": leg_row[3],
                "lots": leg_row[4],
                "no_of_reentry": leg_row[5],
                "option_type": leg_row[6],
                "percent_of_atm_strike_sign": leg_row[7],
                "percent_of_atm_strike_value": leg_row[8],
                "position": leg_row[9],
                "range_breakout": leg_row[10],
                "roll_strike": leg_row[11],
                "roll_strike_increase_in_profit": leg_row[12],
                "roll_strike_lock_profit": leg_row[13],
                "roll_strike_lock_profit_sign": leg_row[14],
                "roll_strike_profit_reaches": leg_row[15],
                "roll_strike_stop_loss": leg_row[16],
                "roll_strike_stop_loss_sign": leg_row[17],
                "roll_strike_strike_type": leg_row[18],
                "roll_strike_trail_profit": leg_row[19],
                "roll_strike_trail_profit_sign": leg_row[20],
                "roll_strike_trailing_options": leg_row[21],
                "simple_momentum": leg_row[22],
                "simple_momentum_direction": leg_row[23],
                "simple_momentum_range_breakout": leg_row[24],
                "simple_momentum_sign": leg_row[25],
                "straddle_width_sign": leg_row[26],
                "straddle_width_value": leg_row[27],
                "strategy_id": leg_row[28],
                "strike_selection_criteria": leg_row[29],
                "strike_selection_criteria_increase_in_profit": leg_row[30],
                "strike_selection_criteria_lock_profit": leg_row[31],
                "strike_selection_criteria_lock_profit_sign": leg_row[32],
                "strike_selection_criteria_profit_reaches": leg_row[33],
                "strike_selection_criteria_stop_loss": leg_row[34],
                "strike_selection_criteria_stop_loss_sign": leg_row[35],
                "strike_selection_criteria_trail_profit": leg_row[36],
                "strike_selection_criteria_trail_profit_sign": leg_row[37],
                "strike_selection_criteria_trailing_options": leg_row[38],
                "strike_type": leg_row[39],
                "expiry": leg_row[40],
                "createdBy" : leg_row[41],
                "createdDate" : leg_row[42],
                "modifiedBy" : leg_row[43],
                "lastUpdatedDateTime" : leg_row[44],
                }
            #print(leg)
            strategy["legs"].append(leg)
                    #print(strategy)
    strategies.append(strategy)
            #print(strategy)
    #data = {"strategies": strategy}
    # = strategies
    if value==1:       
        return strategy
    else:
        return strategies



class StraddleRepo:
    def __init__(self):
        pass
    
    def insert_data(self,strategy_data,legs_data):
       
        #print(strategy_data.id)
       
        mycursor = mydb.cursor()
        query = """
        INSERT INTO strategy (
                name, underlying, strategy_type, implied_futures_expiry, entry_time,
                last_entry_time, exit_time, square_off, overall_sl, overall_target,
                trailing_options, profit_reaches, lock_profit, increase_in_profit, trail_profit, createdBy
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (strategy_data.name,strategy_data.underlying,strategy_data.strategy_type,strategy_data.implied_futures_expiry,strategy_data.entry_time,strategy_data.last_entry_time
                                 ,strategy_data.exit_time,strategy_data.square_off,strategy_data.overall_sl,strategy_data.overall_target,strategy_data.trailing_options,strategy_data.profit_reaches
                                 ,strategy_data.lock_profit,strategy_data.increase_in_profit,strategy_data.trail_profit,strategy_data.createdBy,
        )
        #print(query) 
        mycursor.execute(query, values)
        mydb.commit()
        #print("Data inserted successfully in strategy table.")
        inserted_id = mycursor.lastrowid
        #print("Inserted ID:", inserted_id)
    
            #print(leg_value.strategy_id)
        query= """INSERT INTO leg (strategy_id,leg_no,lots,position,option_type,expiry,no_of_reentry,strike_selection_criteria,closest_premium,strike_type,straddle_width_value,straddle_width_sign,percent_of_atm_strike_value,percent_of_atm_strike_sign,atm_straddle_premium,strike_selection_criteria_stop_loss,strike_selection_criteria_stop_loss_sign,strike_selection_criteria_trailing_options,strike_selection_criteria_profit_reaches,strike_selection_criteria_lock_profit,strike_selection_criteria_lock_profit_sign,strike_selection_criteria_increase_in_profit,strike_selection_criteria_trail_profit,strike_selection_criteria_trail_profit_sign,roll_strike,roll_strike_strike_type,roll_strike_stop_loss,roll_strike_stop_loss_sign,roll_strike_trailing_options,roll_strike_profit_reaches,roll_strike_lock_profit,roll_strike_lock_profit_sign,roll_strike_increase_in_profit,roll_strike_trail_profit,roll_strike_trail_profit_sign,simple_momentum_range_breakout,simple_momentum,simple_momentum_sign,simple_momentum_direction,range_breakout,createdBy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        for leg_value in legs_data:
            values = (inserted_id,leg_value.leg_no,leg_value.lots,leg_value.position,leg_value.option_type,leg_value.expiry,leg_value.no_of_reentry,leg_value.strike_selection_criteria,leg_value.closest_premium,leg_value.strike_type,leg_value.straddle_width_value,leg_value.straddle_width_sign,leg_value.percent_of_atm_strike_value,leg_value.percent_of_atm_strike_sign,leg_value.atm_straddle_premium,leg_value.strike_selection_criteria_stop_loss,leg_value.strike_selection_criteria_stop_loss_sign,leg_value.strike_selection_criteria_trailing_options,leg_value.strike_selection_criteria_profit_reaches,leg_value.strike_selection_criteria_lock_profit,leg_value.strike_selection_criteria_lock_profit_sign,leg_value.strike_selection_criteria_increase_in_profit,leg_value.strike_selection_criteria_trail_profit,leg_value.strike_selection_criteria_trail_profit_sign,leg_value.roll_strike,leg_value.roll_strike_strike_type,leg_value.roll_strike_stop_loss,leg_value.roll_strike_stop_loss_sign,leg_value.roll_strike_trailing_options,leg_value.roll_strike_profit_reaches,leg_value.roll_strike_lock_profit,leg_value.roll_strike_lock_profit_sign,leg_value.roll_strike_increase_in_profit,leg_value.roll_strike_trail_profit,leg_value.roll_strike_trail_profit_sign,leg_value.simple_momentum_range_breakout,leg_value.simple_momentum,leg_value.simple_momentum_sign,leg_value.simple_momentum_direction,leg_value.range_breakout,leg_value.createdBy,)
            #print(query)
            #print(values)
            try:
                mycursor.execute(query, values)
                mydb.commit()
                #print("Insertion successful!")
            except Exception as e:
                print("Error:", e)
            
    def update_data(self, strategy_data, legs_data, strategyId):
        mycursor = mydb.cursor()
    
        # Delete existing leg data for the strategyId
        delete_leg_query = "DELETE FROM leg WHERE strategy_id = %s"
        delete_leg_values = (strategyId,)
        mycursor.execute(delete_leg_query, delete_leg_values)
        mydb.commit()
    
        # Insert new leg data
        for leg_value in legs_data:
            leg_query = """
                INSERT INTO leg (strategy_id, leg_no, lots, position, option_type, expiry, no_of_reentry, strike_selection_criteria, 
                closest_premium, strike_type, straddle_width_value, straddle_width_sign, percent_of_atm_strike_value, 
                percent_of_atm_strike_sign, atm_straddle_premium, strike_selection_criteria_stop_loss, 
                strike_selection_criteria_stop_loss_sign, strike_selection_criteria_trailing_options, 
                strike_selection_criteria_profit_reaches, strike_selection_criteria_lock_profit, 
                strike_selection_criteria_lock_profit_sign, strike_selection_criteria_increase_in_profit, 
                strike_selection_criteria_trail_profit, strike_selection_criteria_trail_profit_sign, roll_strike, 
                roll_strike_strike_type, roll_strike_stop_loss, roll_strike_stop_loss_sign, roll_strike_trailing_options, 
                roll_strike_profit_reaches, roll_strike_lock_profit, roll_strike_lock_profit_sign, roll_strike_increase_in_profit, 
                roll_strike_trail_profit, roll_strike_trail_profit_sign, simple_momentum_range_breakout, simple_momentum, 
                simple_momentum_sign, simple_momentum_direction, range_breakout, modifiedBy)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            leg_values = (strategyId, leg_value.leg_no, leg_value.lots, leg_value.position, leg_value.option_type, leg_value.expiry,
                          leg_value.no_of_reentry, leg_value.strike_selection_criteria, leg_value.closest_premium, leg_value.strike_type,
                          leg_value.straddle_width_value, leg_value.straddle_width_sign, leg_value.percent_of_atm_strike_value,
                          leg_value.percent_of_atm_strike_sign, leg_value.atm_straddle_premium, leg_value.strike_selection_criteria_stop_loss,
                          leg_value.strike_selection_criteria_stop_loss_sign, leg_value.strike_selection_criteria_trailing_options,
                          leg_value.strike_selection_criteria_profit_reaches, leg_value.strike_selection_criteria_lock_profit,
                          leg_value.strike_selection_criteria_lock_profit_sign, leg_value.strike_selection_criteria_increase_in_profit,
                          leg_value.strike_selection_criteria_trail_profit, leg_value.strike_selection_criteria_trail_profit_sign,
                          leg_value.roll_strike, leg_value.roll_strike_strike_type, leg_value.roll_strike_stop_loss,
                          leg_value.roll_strike_stop_loss_sign, leg_value.roll_strike_trailing_options, leg_value.roll_strike_profit_reaches,
                          leg_value.roll_strike_lock_profit, leg_value.roll_strike_lock_profit_sign, leg_value.roll_strike_increase_in_profit,
                          leg_value.roll_strike_trail_profit, leg_value.roll_strike_trail_profit_sign, leg_value.simple_momentum_range_breakout,
                          leg_value.simple_momentum, leg_value.simple_momentum_sign, leg_value.simple_momentum_direction, leg_value.range_breakout, leg_value.modifiedBy)
    
            mycursor.execute(leg_query, leg_values)
            mydb.commit()
    
        # Update strategy table (assuming it remains unchanged)
        update_strategy_query = """
            UPDATE strategy
            SET
                name = %s, underlying = %s, strategy_type = %s, implied_futures_expiry = %s, entry_time = %s,
                last_entry_time = %s, exit_time = %s, square_off = %s, overall_sl = %s, overall_target = %s,
                trailing_options = %s, profit_reaches = %s, lock_profit = %s, increase_in_profit = %s, trail_profit = %s , modifiedBy = %s
            WHERE
                id = %s
            """
        strategy_values = (strategy_data.name, strategy_data.underlying, strategy_data.strategy_type,
                           strategy_data.implied_futures_expiry, strategy_data.entry_time, strategy_data.last_entry_time,
                           strategy_data.exit_time, strategy_data.square_off, strategy_data.overall_sl,
                           strategy_data.overall_target, strategy_data.trailing_options, strategy_data.profit_reaches,
                           strategy_data.lock_profit, strategy_data.increase_in_profit, strategy_data.trail_profit, strategy_data.modifiedBy,strategyId)
        
        mycursor.execute(update_strategy_query, strategy_values)
        mydb.commit()
    
        # Optionally print or log success message
        print("Data updated successfully for strategy ID:", strategyId)
        
    '''
    def update_data(self,strategy_data,legs_data,strategyId):
       
        #print(strategy_data.id)
       
        mycursor = mydb.cursor()
        query = """
        UPDATE strategy
    SET
        name = %s,underlying = %s,strategy_type = %s,implied_futures_expiry = %s,entry_time = %s,
        last_entry_time = %s,exit_time = %s,square_off = %s,overall_sl = %s,overall_target = %s,
        trailing_options = %s,profit_reaches = %s,lock_profit = %s,increase_in_profit = %s,trail_profit = %s
    WHERE
        id = %s
        """
        values = (strategy_data.name,strategy_data.underlying,strategy_data.strategy_type,strategy_data.implied_futures_expiry,strategy_data.entry_time,strategy_data.last_entry_time
                                 ,strategy_data.exit_time,strategy_data.square_off,strategy_data.overall_sl,strategy_data.overall_target,strategy_data.trailing_options,strategy_data.profit_reaches
                                 ,strategy_data.lock_profit,strategy_data.increase_in_profit,strategy_data.trail_profit,strategyId
        )
        #print(query) 
        mycursor.execute(query, values)
        mydb.commit()
        #print("Data inserted successfully in strategy table.")
        inserted_id = mycursor.lastrowid
        #print("Inserted ID:", inserted_id)
            #print(leg_value.strategy_id)
        
        leg_query = """
            UPDATE leg
            SET
                lots = %s, position = %s, option_type = %s, expiry = %s, no_of_reentry = %s, strike_selection_criteria = %s, 
                closest_premium = %s, strike_type = %s, straddle_width_value = %s, straddle_width_sign = %s, 
                percent_of_atm_strike_value = %s, percent_of_atm_strike_sign = %s, atm_straddle_premium = %s, 
                strike_selection_criteria_stop_loss = %s, strike_selection_criteria_stop_loss_sign = %s, 
                strike_selection_criteria_trailing_options = %s, strike_selection_criteria_profit_reaches = %s, 
                strike_selection_criteria_lock_profit = %s, strike_selection_criteria_lock_profit_sign = %s, 
                strike_selection_criteria_increase_in_profit = %s, strike_selection_criteria_trail_profit = %s, 
                strike_selection_criteria_trail_profit_sign = %s, roll_strike = %s, roll_strike_strike_type = %s, 
                roll_strike_stop_loss = %s, roll_strike_stop_loss_sign = %s, roll_strike_trailing_options = %s, 
                roll_strike_profit_reaches = %s, roll_strike_lock_profit = %s, roll_strike_lock_profit_sign = %s, 
                roll_strike_increase_in_profit = %s, roll_strike_trail_profit = %s, roll_strike_trail_profit_sign = %s, 
                simple_momentum_range_breakout = %s, simple_momentum = %s, simple_momentum_sign = %s, 
                simple_momentum_direction = %s, range_breakout = %s
            WHERE
                strategy_id = %s AND id = %s
                """
        for leg_value in legs_data:
        # Fetch leg_id from the database
            leg_id_query = "SELECT id FROM leg WHERE strategy_id = %s AND leg_no = %s"
            leg_id_values = (strategyId, leg_value.leg_no)
            mycursor.execute(leg_id_query, leg_id_values)
            result = mycursor.fetchone()
            if result:
                leg_id = result[0]
            # Now update the leg data using the fetched leg_id
                leg_values = (leg_value.lots, leg_value.position, leg_value.option_type, leg_value.expiry, leg_value.no_of_reentry, leg_value.strike_selection_criteria, 
                          leg_value.closest_premium, leg_value.strike_type, leg_value.straddle_width_value, leg_value.straddle_width_sign, 
                          leg_value.percent_of_atm_strike_value, leg_value.percent_of_atm_strike_sign, leg_value.atm_straddle_premium, 
                          leg_value.strike_selection_criteria_stop_loss, leg_value.strike_selection_criteria_stop_loss_sign, 
                          leg_value.strike_selection_criteria_trailing_options, leg_value.strike_selection_criteria_profit_reaches, 
                          leg_value.strike_selection_criteria_lock_profit, leg_value.strike_selection_criteria_lock_profit_sign, 
                          leg_value.strike_selection_criteria_increase_in_profit, leg_value.strike_selection_criteria_trail_profit, 
                          leg_value.strike_selection_criteria_trail_profit_sign, leg_value.roll_strike, leg_value.roll_strike_strike_type, 
                          leg_value.roll_strike_stop_loss, leg_value.roll_strike_stop_loss_sign, leg_value.roll_strike_trailing_options, 
                          leg_value.roll_strike_profit_reaches, leg_value.roll_strike_lock_profit, leg_value.roll_strike_lock_profit_sign, 
                          leg_value.roll_strike_increase_in_profit, leg_value.roll_strike_trail_profit, leg_value.roll_strike_trail_profit_sign, 
                          leg_value.simple_momentum_range_breakout, leg_value.simple_momentum, leg_value.simple_momentum_sign, 
                          leg_value.simple_momentum_direction, leg_value.range_breakout, strategyId, leg_id)
                mycursor.execute(leg_query, leg_values)
                mydb.commit()
                #print("Update successful for leg data with strategy ID:", strategyId, "and leg ID:", leg_id)
            else:
                print("Leg with leg_no {} not found for strategy with ID {}".format(leg_value.leg_no, strategyId))
    '''    
                
    def getStrategyName(self):
        #print("1")
        strategy_names = []
        mycursor = mydb.cursor()
        query = "SELECT id, name FROM strategy"
        mycursor.execute(query)
        #print("2")
        result = mycursor.fetchall()
        #print(result)
        for row in result:
            strategy = {
                "id": row[0],
                "name": row[1]
            }
            #print(strategy)
            strategy_names.append(strategy)
        #print(strategy_names)
        transformed_data = {"strategies": strategy_names}
        # Outputting the transformed data
        #print(json.dumps(transformed_data, indent=2))
        return strategy_names

    def getStrategyDetails(self, strategy_id):
        #print('3')
        value=1
        mycursor = mydb.cursor(dictionary=True)
        stategy_details = ""
        query =  """
        SELECT *
        FROM strategy
        WHERE strategy.id = %s
        """
        mycursor.execute(query, (strategy_id,))
        result = mycursor.fetchall()
        #print('4')
        stategy_details = convert_to_json(result,strategy_id,value)
        #for row in result:
         #   strategy_details.append(row)
         
    
        return stategy_details
        
    def getAllStrategies(self):
        try:
            mycursor = mydb.cursor(dictionary=True)
            value=2
            # Step 1: Fetch all unique strategy IDs
            mycursor.execute("SELECT DISTINCT id FROM strategy")
            strategy_ids = [row['id'] for row in mycursor.fetchall()]
            
            # List to store all strategy details
            all_strategies = []
            
            # Step 2: Iterate over each strategy_id and fetch details
            for strategy_id in strategy_ids:
                # Fetch strategy details
                query = """
                SELECT *
                FROM strategy
                WHERE strategy.id = %s
                """
                mycursor.execute(query, (strategy_id,))
                result = mycursor.fetchall()
                
                # Convert to JSON format
                strategy_details = convert_to_json(result, strategy_id,value)
                # Append strategy details to all_strategies list
                #return strategy_details
                
                all_strategies.extend(strategy_details)
                #all_strategies.append(result)
            
            # Return all strategies as JSON data
            transformed_data = {"strategies": all_strategies}
            # Outputting the transformed data
            #print(json.dumps(transformed_data, indent=2))
            return all_strategies
        
        except Exception as e:
            print(f"Rupendra 2 Error retrieving strategy details: {e}")
            return {"error": str(e)}

            
    
    