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
    raise HTTPException(status_code=500, detail="Failed to import common_function")

# Set environment and key to fetch DB configuration
env = "dev"  # Example environment, e.g., 'dev', 'prod'
key = "db_sagar_strategy"  # Example key to fetch DB configuration

# Fetch the database configuration
db_Value = fetch_parameter(env, key)

# Handle case if the db_Value is None
if db_Value is None:
    raise HTTPException(status_code=500, detail="Failed to fetch database configuration.")
else:
    print(f"Fetched db config: {db_Value}")

# Define DB_CONNECTION_PARAMS dynamically
DB_CONNECTION_PARAMS = {
    'host': db_Value['host'],
    'user': db_Value['user'],
    'password': db_Value['password'],
    'db': db_Value['database']
}

mydb = mysql.connector.connect(
    host=db_Value['host'],
    user=db_Value['user'],
    password=db_Value['password'],
    database=db_Value['database']
)

def convert_legs_to_json(result,statVarId):
    variables = []
    connection = mysql.connector.connect(
      **DB_CONNECTION_PARAMS
      )

    if connection.is_connected():
        mycursor = connection.cursor(dictionary=True)
        
        for var in result:
            strategyvariables = {
                "id": statVarId,
                "portfolio_strategy_id": var["portfolio_strategy_id"],
                "underlying": var["underlying"],
                "strategy_type": var["strategy_type"],
                "quantity_multiplier": var["quantity_multiplier"],
                "implied_futures_expiry": var["implied_futures_expiry"],
                "entry_time": var["entry_time"],
                "last_entry_time": var["last_entry_time"],
                "exit_time": var["exit_time"],
                "square_off": var["square_off"],
                "overall_sl": var["overall_sl"],
                "overall_target": var["overall_target"],
                "trailing_options": var["trailing_options"],
                "profit_reaches": var["profit_reaches"],
                "lock_profit": var["lock_profit"],
                "increase_in_profit": var["increase_in_profit"],
                "trail_profit": var["trail_profit"],
                "legs": []
            }
            
            leg_var_query = """SELECT id, portfolio_strategy_variables_id, lots, position, option_type, expiry, no_of_reentry,
                                      strike_selection_criteria, closest_premium, strike_type, straddle_width_value, straddle_width_sign,
                                      percent_of_atm_strike_value, percent_of_atm_strike_sign, atm_straddle_premium,
                                      strike_selection_criteria_stop_loss, strike_selection_criteria_stop_loss_sign,
                                      strike_selection_criteria_trailing_options, strike_selection_criteria_profit_reaches,
                                      strike_selection_criteria_lock_profit, strike_selection_criteria_lock_profit_sign,
                                      strike_selection_criteria_increase_in_profit, strike_selection_criteria_trail_profit,
                                      strike_selection_criteria_trail_profit_sign, roll_strike, roll_strike_strike_type,
                                      roll_strike_stop_loss, roll_strike_stop_loss_sign, roll_strike_trailing_options,
                                      roll_strike_profit_reaches, roll_strike_lock_profit, roll_strike_lock_profit_sign,
                                      roll_strike_increase_in_profit, roll_strike_trail_profit, roll_strike_trail_profit_sign,
                                      simple_momentum_range_breakout, simple_momentum, simple_momentum_sign, simple_momentum_direction,
                                      range_breakout 
                               FROM portfoliostrategyvariableslegs 
                               WHERE portfolio_strategy_variables_id = %s"""
            mycursor.execute(leg_var_query, (statVarId,))
            leg_values = mycursor.fetchall()
            
            for leg_value in leg_values:
                legs = {
                    "id": leg_value["id"],
                    "portfolio_strategy_variables_id": leg_value["portfolio_strategy_variables_id"],
                    "lots": leg_value["lots"],
                    "position": leg_value["position"],
                    "option_type": leg_value["option_type"],
                    "expiry": leg_value["expiry"],
                    "no_of_reentry": leg_value["no_of_reentry"],
                    "strike_selection_criteria": leg_value["strike_selection_criteria"],
                    "closest_premium": leg_value["closest_premium"],
                    "strike_type": leg_value["strike_type"],
                    "straddle_width_value": leg_value["straddle_width_value"],
                    "straddle_width_sign": leg_value["straddle_width_sign"],
                    "percent_of_atm_strike_value": leg_value["percent_of_atm_strike_value"],
                    "percent_of_atm_strike_sign": leg_value["percent_of_atm_strike_sign"],
                    "atm_straddle_premium": leg_value["atm_straddle_premium"],
                    "strike_selection_criteria_stop_loss": leg_value["strike_selection_criteria_stop_loss"],
                    "strike_selection_criteria_stop_loss_sign": leg_value["strike_selection_criteria_stop_loss_sign"],
                    "strike_selection_criteria_trailing_options": leg_value["strike_selection_criteria_trailing_options"],
                    "strike_selection_criteria_profit_reaches": leg_value["strike_selection_criteria_profit_reaches"],
                    "strike_selection_criteria_lock_profit": leg_value["strike_selection_criteria_lock_profit"],
                    "strike_selection_criteria_lock_profit_sign": leg_value["strike_selection_criteria_lock_profit_sign"],
                    "strike_selection_criteria_increase_in_profit": leg_value["strike_selection_criteria_increase_in_profit"],
                    "strike_selection_criteria_trail_profit": leg_value["strike_selection_criteria_trail_profit"],
                    "strike_selection_criteria_trail_profit_sign": leg_value["strike_selection_criteria_trail_profit_sign"],
                    "roll_strike": leg_value["roll_strike"],
                    "roll_strike_strike_type": leg_value["roll_strike_strike_type"],
                    "roll_strike_stop_loss": leg_value["roll_strike_stop_loss"],
                    "roll_strike_stop_loss_sign": leg_value["roll_strike_stop_loss_sign"],
                    "roll_strike_trailing_options": leg_value["roll_strike_trailing_options"],
                    "roll_strike_profit_reaches": leg_value["roll_strike_profit_reaches"],
                    "roll_strike_lock_profit": leg_value["roll_strike_lock_profit"],
                    "roll_strike_lock_profit_sign": leg_value["roll_strike_lock_profit_sign"],
                    "roll_strike_increase_in_profit": leg_value["roll_strike_increase_in_profit"],
                    "roll_strike_trail_profit": leg_value["roll_strike_trail_profit"],
                    "roll_strike_trail_profit_sign": leg_value["roll_strike_trail_profit_sign"],
                    "simple_momentum_range_breakout": leg_value["simple_momentum_range_breakout"],
                    "simple_momentum": leg_value["simple_momentum"],
                    "simple_momentum_sign": leg_value["simple_momentum_sign"],
                    "simple_momentum_direction": leg_value["simple_momentum_direction"],
                    "range_breakout": leg_value["range_breakout"]
                }
                strategyvariables["legs"].append(legs)
            
            variables.append(strategyvariables)
        return variables

def convert_to_json(result, portfolio_id, value):
    portfolios = []
    connection = mysql.connector.connect(
      **DB_CONNECTION_PARAMS
      )

    if connection.is_connected():
        mycursor = connection.cursor(dictionary=True)

        for row in result:
            strategy = {
                "id": row["id"],
                "name": row["name"],
                "createdBy": row["createdBy"],
                "createdDate": row["createdDate"],
                "modifiedBy": row["modifiedBy"],
                "lastUpdatedDateTime": row["lastUpdatedDateTime"],
                "strategies": []
            }
            
            leg_sql = """SELECT id, portfolio_Id, strategy_id, symbol, quantity_multiplier, monday, tuesday, wednesday, thrusday, friday,createdBy,createdDate,modifiedBy,lastUpdatedDateTime
                         FROM portfoliostrategies 
                         WHERE portfolio_Id = %s"""
            mycursor.execute(leg_sql, (portfolio_id,))
            leg_rows = mycursor.fetchall()
            
            for leg_row in leg_rows:
                strategies = {
                    "id": leg_row["id"],
                    "portfolio_Id": leg_row["portfolio_Id"],
                    "strategy_id": leg_row["strategy_id"],
                    "symbol": leg_row["symbol"],
                    "quantity_multiplier": leg_row["quantity_multiplier"],
                    "monday": bool(leg_row["monday"]),
                    "tuesday": bool(leg_row["tuesday"]),
                    "wednesday": bool(leg_row["wednesday"]),
                    "thrusday": bool(leg_row["thrusday"]),
                    "friday": bool(leg_row["friday"]),
                    "createdBy": leg_row["createdBy"],
                    "createdDate": leg_row["createdDate"],
                    "modifiedBy": leg_row["modifiedBy"],
                    "lastUpdatedDateTime": leg_row["lastUpdatedDateTime"],
                    "strategyvariables": {}
                }
                
                var_query = """SELECT id, portfolio_strategy_id, underlying, strategy_type, quantity_multiplier, implied_futures_expiry,
                                      entry_time, last_entry_time, exit_time, square_off, overall_sl, overall_target, trailing_options,
                                      profit_reaches, lock_profit, increase_in_profit, trail_profit ,createdBy,createdDate,modifiedBy,lastUpdatedDateTime
                               FROM portfoliostrategyvariables 
                               WHERE portfolio_strategy_id = %s"""
                mycursor.execute(var_query, (leg_row["id"],))
                var = mycursor.fetchone()
                
                if var:
                    strategyvariables = {
                        "id": var["id"],
                        "portfolio_strategy_id": var["portfolio_strategy_id"],
                        "underlying": var["underlying"],
                        "strategy_type": var["strategy_type"],
                        "quantity_multiplier": var["quantity_multiplier"],
                        "implied_futures_expiry": var["implied_futures_expiry"],
                        "entry_time": var["entry_time"],
                        "last_entry_time": var["last_entry_time"],
                        "exit_time": var["exit_time"],
                        "square_off": var["square_off"],
                        "overall_sl": var["overall_sl"],
                        "overall_target": var["overall_target"],
                        "trailing_options": var["trailing_options"],
                        "profit_reaches": var["profit_reaches"],
                        "lock_profit": var["lock_profit"],
                        "increase_in_profit": var["increase_in_profit"],
                        "trail_profit": var["trail_profit"],
                        "createdBy": var["createdBy"],
                        "createdDate": var["createdDate"],
                        "modifiedBy": var["modifiedBy"],
                        "lastUpdatedDateTime": var["lastUpdatedDateTime"],
                        "legs": []
                    }
                    
                    leg_var_query = """SELECT id, portfolio_strategy_variables_id, lots, position, option_type, expiry, no_of_reentry,
                                              strike_selection_criteria, closest_premium, strike_type, straddle_width_value, straddle_width_sign,
                                              percent_of_atm_strike_value, percent_of_atm_strike_sign, atm_straddle_premium,
                                              strike_selection_criteria_stop_loss, strike_selection_criteria_stop_loss_sign,
                                              strike_selection_criteria_trailing_options, strike_selection_criteria_profit_reaches,
                                              strike_selection_criteria_lock_profit, strike_selection_criteria_lock_profit_sign,
                                              strike_selection_criteria_increase_in_profit, strike_selection_criteria_trail_profit,
                                              strike_selection_criteria_trail_profit_sign, roll_strike, roll_strike_strike_type,
                                              roll_strike_stop_loss, roll_strike_stop_loss_sign, roll_strike_trailing_options,
                                              roll_strike_profit_reaches, roll_strike_lock_profit, roll_strike_lock_profit_sign,
                                              roll_strike_increase_in_profit, roll_strike_trail_profit, roll_strike_trail_profit_sign,
                                              simple_momentum_range_breakout, simple_momentum, simple_momentum_sign, simple_momentum_direction,
                                              range_breakout ,createdBy,createdDate,modifiedBy,lastUpdatedDateTime
                                       FROM portfoliostrategyvariableslegs 
                                       WHERE portfolio_strategy_variables_id = %s"""
                    mycursor.execute(leg_var_query, (var["id"],))
                    leg_values = mycursor.fetchall()
                    
                    for leg_value in leg_values:
                        legs = {
                            "id": leg_value["id"],
                            "portfolio_strategy_variables_id": leg_value["portfolio_strategy_variables_id"],
                            "lots": leg_value["lots"],
                            "position": leg_value["position"],
                            "option_type": leg_value["option_type"],
                            "expiry": leg_value["expiry"],
                            "no_of_reentry": leg_value["no_of_reentry"],
                            "strike_selection_criteria": leg_value["strike_selection_criteria"],
                            "closest_premium": leg_value["closest_premium"],
                            "strike_type": leg_value["strike_type"],
                            "straddle_width_value": leg_value["straddle_width_value"],
                            "straddle_width_sign": leg_value["straddle_width_sign"],
                            "percent_of_atm_strike_value": leg_value["percent_of_atm_strike_value"],
                            "percent_of_atm_strike_sign": leg_value["percent_of_atm_strike_sign"],
                            "atm_straddle_premium": leg_value["atm_straddle_premium"],
                            "strike_selection_criteria_stop_loss": leg_value["strike_selection_criteria_stop_loss"],
                            "strike_selection_criteria_stop_loss_sign": leg_value["strike_selection_criteria_stop_loss_sign"],
                            "strike_selection_criteria_trailing_options": leg_value["strike_selection_criteria_trailing_options"],
                            "strike_selection_criteria_profit_reaches": leg_value["strike_selection_criteria_profit_reaches"],
                            "strike_selection_criteria_lock_profit": leg_value["strike_selection_criteria_lock_profit"],
                            "strike_selection_criteria_lock_profit_sign": leg_value["strike_selection_criteria_lock_profit_sign"],
                            "strike_selection_criteria_increase_in_profit": leg_value["strike_selection_criteria_increase_in_profit"],
                            "strike_selection_criteria_trail_profit": leg_value["strike_selection_criteria_trail_profit"],
                            "strike_selection_criteria_trail_profit_sign": leg_value["strike_selection_criteria_trail_profit_sign"],
                            "roll_strike": leg_value["roll_strike"],
                            "roll_strike_strike_type": leg_value["roll_strike_strike_type"],
                            "roll_strike_stop_loss": leg_value["roll_strike_stop_loss"],
                            "roll_strike_stop_loss_sign": leg_value["roll_strike_stop_loss_sign"],
                            "roll_strike_trailing_options": leg_value["roll_strike_trailing_options"],
                            "roll_strike_profit_reaches": leg_value["roll_strike_profit_reaches"],
                            "roll_strike_lock_profit": leg_value["roll_strike_lock_profit"],
                            "roll_strike_lock_profit_sign": leg_value["roll_strike_lock_profit_sign"],
                            "roll_strike_increase_in_profit": leg_value["roll_strike_increase_in_profit"],
                            "roll_strike_trail_profit": leg_value["roll_strike_trail_profit"],
                            "roll_strike_trail_profit_sign": leg_value["roll_strike_trail_profit_sign"],
                            "simple_momentum_range_breakout": leg_value["simple_momentum_range_breakout"],
                            "simple_momentum": leg_value["simple_momentum"],
                            "simple_momentum_sign": leg_value["simple_momentum_sign"],
                            "simple_momentum_direction": leg_value["simple_momentum_direction"],
                            "range_breakout": leg_value["range_breakout"],
                            "createdBy": leg_value["createdBy"],
                            "createdDate": leg_value["createdDate"],
                            "modifiedBy": leg_value["modifiedBy"],
                            "lastUpdatedDateTime": leg_value["lastUpdatedDateTime"]
                        }
                        strategyvariables["legs"].append(legs)
                    
                    strategies["strategyvariables"] = strategyvariables
                strategy["strategies"].append(strategies)
    
            portfolios.append(strategy)
        
        if value == 1:
            return strategy
        else:
            return portfolios

def insert_strategy(strategies,strategyvariables,legs,portfolio_id):
    mycursor = mydb.cursor()
    
    for strategy in strategies:
        query = """
            INSERT INTO portfoliostrategies (portfolio_id, strategy_id, symbol, quantity_multiplier, monday, tuesday, wednesday, thrusday, friday, createdBy)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            portfolio_id,
            strategy.strategy_id,
            strategy.symbol,
            strategy.quantity_multiplier,
            strategy.monday,
            strategy.tuesday,
            strategy.wednesday,
            strategy.thrusday,  # corrected spelling of 'thursday'
            strategy.friday,
            strategy.createdBy,

        )
        try:
            mycursor.execute(query, values)
            mydb.commit()
            print("Insertion successful into portfoliostrategies table!")
            strategy_id = mycursor.lastrowid  # Get the inserted strategy_id
            print(strategy_id)
            for variable in strategyvariables:
                query = """
                        INSERT INTO portfoliostrategyvariables (
                            portfolio_strategy_id, underlying, strategy_type, quantity_multiplier, implied_futures_expiry,
                            entry_time, last_entry_time, exit_time, square_off, overall_sl, overall_target, trailing_options,
                            profit_reaches, lock_profit, increase_in_profit, trail_profit,createdBy
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                values = (
                        strategy_id,  # Use the strategy_id as portfolio_strategy_id
                        variable.underlying,
                        variable.strategy_type,
                        variable.quantity_multiplier,
                        variable.implied_futures_expiry,
                        variable.entry_time,
                        variable.last_entry_time,
                        variable.exit_time,
                        variable.square_off,
                        variable.overall_sl,
                        variable.overall_target,
                        variable.trailing_options,
                        variable.profit_reaches,
                        variable.lock_profit,
                        variable.increase_in_profit,
                        variable.trail_profit,
                        variable.createdBy
                    )
                try:
                    mycursor.execute(query, values)
                    mydb.commit()
                    print("Insertion successful into portfoliostrategyvariables table!")
                    portfolio_strategy_id = mycursor.lastrowid  # Get the inserted portfolio_strategy_id
                    print("Portfolio Strategy ID:", portfolio_strategy_id)
                    for leg_value in legs:
                        created_by_value = leg_value.createdBy[0] if isinstance(leg_value.createdBy, (tuple, list)) and leg_value.createdBy else leg_value.createdBy
                        try:
                            # Prepare the SQL query
                            query = """
                                INSERT INTO portfoliostrategyvariableslegs (
                                    portfolio_strategy_variables_id, lots, position, option_type, expiry, no_of_reentry,
                                    strike_selection_criteria, closest_premium, strike_type, straddle_width_value, straddle_width_sign,
                                    percent_of_atm_strike_value, percent_of_atm_strike_sign, atm_straddle_premium,
                                    strike_selection_criteria_stop_loss, strike_selection_criteria_stop_loss_sign,
                                    strike_selection_criteria_trailing_options, strike_selection_criteria_profit_reaches,
                                    strike_selection_criteria_lock_profit, strike_selection_criteria_lock_profit_sign,
                                    strike_selection_criteria_increase_in_profit, strike_selection_criteria_trail_profit,
                                    strike_selection_criteria_trail_profit_sign, roll_strike, roll_strike_strike_type,
                                    roll_strike_stop_loss, roll_strike_stop_loss_sign, roll_strike_trailing_options,
                                    roll_strike_profit_reaches, roll_strike_lock_profit, roll_strike_lock_profit_sign,
                                    roll_strike_increase_in_profit, roll_strike_trail_profit, roll_strike_trail_profit_sign,
                                    simple_momentum_range_breakout, simple_momentum, simple_momentum_sign, simple_momentum_direction,
                                    range_breakout, createdBy
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            
                            # Debug: Check the leg_value attributes
                            print(f"Leg Value: {leg_value}")
                            
                            # Create the values tuple to insert
                            values = (
                                portfolio_strategy_id,
                                leg_value.lots,
                                leg_value.position,
                                leg_value.option_type,
                                leg_value.expiry,
                                leg_value.no_of_reentry,
                                leg_value.strike_selection_criteria,
                                leg_value.closest_premium,
                                leg_value.strike_type,
                                leg_value.straddle_width_value,
                                leg_value.straddle_width_sign,
                                leg_value.percent_of_atm_strike_value,
                                leg_value.percent_of_atm_strike_sign,
                                leg_value.atm_straddle_premium,
                                leg_value.strike_selection_criteria_stop_loss,
                                leg_value.strike_selection_criteria_stop_loss_sign,
                                leg_value.strike_selection_criteria_trailing_options,
                                leg_value.strike_selection_criteria_profit_reaches,
                                leg_value.strike_selection_criteria_lock_profit,
                                leg_value.strike_selection_criteria_lock_profit_sign,
                                leg_value.strike_selection_criteria_increase_in_profit,
                                leg_value.strike_selection_criteria_trail_profit,
                                leg_value.strike_selection_criteria_trail_profit_sign,
                                leg_value.roll_strike,
                                leg_value.roll_strike_strike_type,
                                leg_value.roll_strike_stop_loss,
                                leg_value.roll_strike_stop_loss_sign,
                                leg_value.roll_strike_trailing_options,
                                leg_value.roll_strike_profit_reaches,
                                leg_value.roll_strike_lock_profit,
                                leg_value.roll_strike_lock_profit_sign,
                                leg_value.roll_strike_increase_in_profit,
                                leg_value.roll_strike_trail_profit,
                                leg_value.roll_strike_trail_profit_sign,
                                leg_value.simple_momentum_range_breakout,
                                leg_value.simple_momentum,
                                leg_value.simple_momentum_sign,
                                leg_value.simple_momentum_direction,
                                leg_value.range_breakout,
                                created_by_value
                            )

                            # Debug: Print the values to check the format
                            print(f"Values: {values}")
                            
                            # Execute the query and commit the transaction
                            mycursor.execute(query, values)
                            mydb.commit()
                            print(f"Insertion successful into leg table! Portfolio Strategy ID: {portfolio_strategy_id}")
                        
                        except Exception as e:
                            print(f"Error inserting into leg table for Portfolio Strategy ID {portfolio_strategy_id}: {e}")
                            return
                except Exception as e:
                    print("Error inserting into portfoliostrategyvariables table:", e)
                    return
        except Exception as e:
            print("Error inserting into portfoliostrategies table:", e)
            return



def update_Strategy(strategies,portId):
    mycursor = mydb.cursor()
    json_id = []
    query = "SELECT strategy_id from portfoliostrategies WHERE portfolio_id=%s"
    mycursor.execute(query, (portId,))
    result = mycursor.fetchall()
    table_ids = [row[0] for row in result]
    #print(table_ids)
    #print(result)
    for strategy in strategies:
        json_id.append(strategy.strategy_id)
    #print(json_id)
    integer_list = [int(item) for item in json_id]
    #print(integer_list[0])
    
    if integer_list[0] not in table_ids:
        print(integer_list[0])
        query = "DELETE from portfoliostrategies where portfolio_id=%s and strategy_id=%s"
        mycursor.execute(query, (portId,integer_list[0],))
        print("Data updated successfully in portfolio table")
    
    
def update_legs(leg_value,last_id,leg_ids,portfolio_strategy_variable_id):
    print("Updating id is : ",str(last_id))
    mycursor = mydb.cursor()
    query = """
    UPDATE portfoliostrategyvariableslegs 
    SET lots = %s,position = %s,option_type = %s,expiry = %s,no_of_reentry = %s,strike_selection_criteria = %s,closest_premium = %s,strike_type = %s,
            straddle_width_value = %s,straddle_width_sign = %s,percent_of_atm_strike_value = %s,percent_of_atm_strike_sign = %s,
            atm_straddle_premium = %s,strike_selection_criteria_stop_loss = %s,strike_selection_criteria_stop_loss_sign = %s,strike_selection_criteria_trailing_options = %s,
            strike_selection_criteria_profit_reaches = %s,strike_selection_criteria_lock_profit = %s,strike_selection_criteria_lock_profit_sign = %s,
            strike_selection_criteria_increase_in_profit = %s,strike_selection_criteria_trail_profit = %s,strike_selection_criteria_trail_profit_sign = %s,
            roll_strike = %s,roll_strike_strike_type = %s,roll_strike_stop_loss = %s,roll_strike_stop_loss_sign = %s,roll_strike_trailing_options = %s,roll_strike_profit_reaches = %s,
            roll_strike_lock_profit = %s,roll_strike_lock_profit_sign = %s,roll_strike_increase_in_profit = %s,roll_strike_trail_profit = %s,
            roll_strike_trail_profit_sign = %s,simple_momentum_range_breakout = %s,simple_momentum = %s,simple_momentum_sign = %s,
            simple_momentum_direction = %s,range_breakout = %s,modifiedBy = %s
        WHERE portfolio_strategy_variables_id = %s AND id = %s
    """
    # Prepare the values for the UPDATE query
    values = (
            leg_value.get('lots'),
            leg_value.get('position'),
            leg_value.get('option_type'),
            leg_value.get('expiry'),
            leg_value.get('no_of_reentry'),
            leg_value.get('strike_selection_criteria'),
            leg_value.get('closest_premium'),
            leg_value.get('strike_type'),
            leg_value.get('straddle_width_value'),
            leg_value.get('straddle_width_sign'),
            leg_value.get('percent_of_atm_strike_value'),
            leg_value.get('percent_of_atm_strike_sign'),
            leg_value.get('atm_straddle_premium'),
            leg_value.get('strike_selection_criteria_stop_loss'),
            leg_value.get('strike_selection_criteria_stop_loss_sign'),
            leg_value.get('strike_selection_criteria_trailing_options'),
            leg_value.get('strike_selection_criteria_profit_reaches'),
            leg_value.get('strike_selection_criteria_lock_profit'),
            leg_value.get('strike_selection_criteria_lock_profit_sign'),
            leg_value.get('strike_selection_criteria_increase_in_profit'),
            leg_value.get('strike_selection_criteria_trail_profit'),
            leg_value.get('strike_selection_criteria_trail_profit_sign'),
            leg_value.get('roll_strike'),
            leg_value.get('roll_strike_strike_type'),
            leg_value.get('roll_strike_stop_loss'),
            leg_value.get('roll_strike_stop_loss_sign'),
            leg_value.get('roll_strike_trailing_options'),
            leg_value.get('roll_strike_profit_reaches'),
            leg_value.get('roll_strike_lock_profit'),
            leg_value.get('roll_strike_lock_profit_sign'),
            leg_value.get('roll_strike_increase_in_profit'),
            leg_value.get('roll_strike_trail_profit'),
            leg_value.get('roll_strike_trail_profit_sign'),
            leg_value.get('simple_momentum_range_breakout'),
            leg_value.get('simple_momentum'),
            leg_value.get('simple_momentum_sign'),
            leg_value.get('simple_momentum_direction'),
            leg_value.get('range_breakout'),
            leg_value.get('modifiedBy'),
            portfolio_strategy_variable_id,  # Assuming you are using this as a condition
            last_id     # Assuming this is the identifier for the row to update
        )
        
        # Execute the UPDATE query
    mycursor.execute(query, values)
    mydb.commit()
    print("Update successful in portfoliostrategyvariableslegs table!")
    leg_ids.remove(last_id)
    return leg_ids
    

class PortfolioRepo:
    def __init__(self):
        pass
    
    def update_portfolio(self,portfolio,portId):
        mycursor = mydb.cursor()
        
        check_query = "SELECT COUNT(*) FROM portfolio WHERE id = %s"
        mycursor.execute(check_query, (portId,))
        result = mycursor.fetchone()
        # print(result[0])
        
        query = "UPDATE portfolio SET name = %s, modifiedBy = %s WHERE id = %s"
        try:
            name_value = (portfolio.name,portfolio.modifiedBy,portId)
            mycursor.execute(query, name_value)
            mydb.commit()
            print("Data updated successfully in portfolio table.")
        except Exception as e:
            print("Error updating portfolio table:", e)
            return
    
    def portfolio_strategy_insert_update(self,strategy_data,portId):
        mycursor = mydb.cursor()
        #print(strategy_data)
        query = "SELECT strategy_id,id from portfoliostrategies where portfolio_id=%s"
        mycursor.execute(query, (portId,))
        result = mycursor.fetchall()
        #print(result)
        ids_in_data = {item[0] for item in result}
        print(ids_in_data)
        main_id = strategy_data['strategy_id']
        json_id = int(main_id)
        print("json id : " ,json_id)
        if json_id in ids_in_data:
            print("update")
            query = """
            UPDATE portfoliostrategies SET symbol = %s, quantity_multiplier = %s, monday = %s, tuesday = %s, wednesday = %s, thrusday = %s, friday = %s, modifiedBy=%s
            WHERE portfolio_id = %s AND strategy_id = %s
            """
            values = (
                strategy_data.get('symbol', None),
                strategy_data.get('quantity_multiplier', None),
                strategy_data.get('monday', None),
                strategy_data.get('tuesday', None),
                strategy_data.get('wednesday', None),
                strategy_data.get('thrusday', None),  # Corrected spelling
                strategy_data.get('friday', None),
                strategy_data.get('modifiedBy', 0),
                portId,
                json_id
            )
            mycursor.execute(query, values)
            mydb.commit()
            print("Update successful in portfoliostrategies table!")
            #return last_id
            query = "SELECT id from portfoliostrategies WHERE portfolio_id = %s AND strategy_id = %s"
            mycursor.execute(query, (portId,json_id))
            result = mycursor.fetchall()
            last_id = result[0][0]
            print(last_id)
        else:
            print("insert")
            query = """
                INSERT INTO portfoliostrategies (portfolio_id, strategy_id, symbol, quantity_multiplier, monday, tuesday, wednesday, thrusday, friday,createdBy)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                portId,
                json_id,
                strategy_data.get('symbol', None),
                strategy_data.get('quantity_multiplier', None),
                strategy_data.get('monday', None),
                strategy_data.get('tuesday', None),
                strategy_data.get('wednesday', None),
                strategy_data.get('thursday', None),  # Corrected spelling
                strategy_data.get('friday', None),
                strategy_data.get('createdBy', 0)
            )
            mycursor.execute(query, values)
            mydb.commit()
            print("Insertion successful into portfoliostrategies table!")
            
            last_id = mycursor.lastrowid  # Get the inserted strategy_id
            print(last_id)
        return last_id
       
    def portfolio_strategy_variable_insert_update(self,variable, strategy_id):
        mycursor = mydb.cursor()
        query = "SELECT id from portfoliostrategyvariables where portfolio_strategy_id = %s"
        mycursor.execute(query, (strategy_id,))
        result = mycursor.fetchall()
        mydb.commit()
        #print(result)
        
        #print(result)
        if result:
            last_id = result[0][0]  # Get the first element of the first tuple
            print(last_id)
            query = """
            UPDATE portfoliostrategyvariables SET underlying = %s, strategy_type = %s, quantity_multiplier = %s, implied_futures_expiry = %s, entry_time = %s, last_entry_time = %s, exit_time = %s,
            square_off = %s, overall_sl = %s, overall_target = %s, trailing_options = %s, profit_reaches = %s, increase_in_profit = %s, trail_profit = %s,modifiedBy=%s
            WHERE  portfolio_strategy_id = %s and id = %s
            """
            values = (
               variable.get('underlying'),
               variable.get('strategy_type'),
               variable.get('quantity_multiplier'),
               variable.get('implied_futures_expiry'),
               variable.get('entry_time'),
               variable.get('last_entry_time'),
               variable.get('exit_time'),
               variable.get('square_off'),
               variable.get('overall_sl'),
               variable.get('overall_target'),
               variable.get('trailing_options'),
               variable.get('profit_reaches'),
               variable.get('increase_in_profit'),
               variable.get('trail_profit'),
               variable.get('modifiedBy'),
               strategy_id,
               last_id
            )
            mycursor.execute(query, values)
            mydb.commit()
            print("Update successful in portfoliostrategyvariables table!")
        else:
            last_id = None
            query = """
                    INSERT INTO portfoliostrategyvariables (
                        portfolio_strategy_id, underlying, strategy_type, quantity_multiplier, implied_futures_expiry,
                        entry_time, last_entry_time, exit_time, square_off, overall_sl, overall_target, trailing_options,
                        profit_reaches, lock_profit, increase_in_profit, trail_profit,createdBy
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                """
            values = (
                    strategy_id,  # Use the strategy_id as portfolio_strategy_id
                    variable.get('underlying'),
                    variable.get('strategy_type'),
                    variable.get('quantity_multiplier'),
                    variable.get('implied_futures_expiry'),
                    variable.get('entry_time'),
                    variable.get('last_entry_time'),
                    variable.get('exit_time'),
                    variable.get('square_off'),
                    variable.get('overall_sl'),
                    variable.get('overall_target'),
                    variable.get('trailing_options'),
                    variable.get('profit_reaches'),
                    variable.get('lock_profit'),
                    variable.get('increase_in_profit'),
                    variable.get('trail_profit'),
                    variable.get('createdBy'),
                )
            
            mycursor.execute(query, values)
            mydb.commit()
            print("Insertion successful into portfoliostrategyvariables table!")
            last_id = mycursor.lastrowid  # Get the inserted portfolio_strategy_id
            print("Portfolio Strategy Variable ID:", last_id)
        return last_id
        
    def update_variables(self,variable, statVarId):
        mycursor = mydb.cursor()
        
        if statVarId:
            #print(2)
            query = """
            UPDATE portfoliostrategyvariables SET underlying = %s, strategy_type = %s, quantity_multiplier = %s, implied_futures_expiry = %s, entry_time = %s, last_entry_time = %s, exit_time = %s,
            square_off = %s, overall_sl = %s, overall_target = %s, trailing_options = %s, profit_reaches = %s, increase_in_profit = %s, trail_profit = %s, modifiedBy=%s
            WHERE id = %s
            """
            values = (
               variable.get('underlying'),
               variable.get('strategy_type'),
               variable.get('quantity_multiplier'),
               variable.get('implied_futures_expiry'),
               variable.get('entry_time'),
               variable.get('last_entry_time'),
               variable.get('exit_time'),
               variable.get('square_off'),
               variable.get('overall_sl'),
               variable.get('overall_target'),
               variable.get('trailing_options'),
               variable.get('profit_reaches'),
               variable.get('increase_in_profit'),
               variable.get('trail_profit'),
               variable.get('modifiedBy'),
               statVarId
            )
            mycursor.execute(query, values)
            mydb.commit()
            #print(4)
            print("Update successful in portfoliostrategyvariables table!")

            
    
    def portfolio_strategy_variable_leg_insert_update(self,leg_values,portfolio_strategy_variable_id):
        mycursor = mydb.cursor()
        leg_ids =[]
        query = "SELECT id from portfoliostrategyvariableslegs where portfolio_strategy_variables_id = %s"
        mycursor.execute(query, (portfolio_strategy_variable_id,))
        result = mycursor.fetchall()
        #print(result)
        mydb.commit()
        for value in result:
            leg_ids.append(value[0])
        
        #print(leg_ids)
        for leg_value in leg_values:
            if len(leg_ids) != 0:
                last_id = leg_ids[0]
                #print(last_id)
                leg_ids = update_legs(leg_value,last_id,leg_ids,portfolio_strategy_variable_id)
                print("Updated legs from db ")
                print(leg_ids)
            else:
                last_id = None
                query = """
                            INSERT INTO portfoliostrategyvariableslegs (
                                portfolio_strategy_variables_id, lots, position, option_type, expiry, no_of_reentry,
                                strike_selection_criteria, closest_premium, strike_type, straddle_width_value, straddle_width_sign,
                                percent_of_atm_strike_value, percent_of_atm_strike_sign, atm_straddle_premium,
                                strike_selection_criteria_stop_loss, strike_selection_criteria_stop_loss_sign,
                                strike_selection_criteria_trailing_options, strike_selection_criteria_profit_reaches,
                                strike_selection_criteria_lock_profit, strike_selection_criteria_lock_profit_sign,
                                strike_selection_criteria_increase_in_profit, strike_selection_criteria_trail_profit,
                                strike_selection_criteria_trail_profit_sign, roll_strike, roll_strike_strike_type,
                                roll_strike_stop_loss, roll_strike_stop_loss_sign, roll_strike_trailing_options,
                                roll_strike_profit_reaches, roll_strike_lock_profit, roll_strike_lock_profit_sign,
                                roll_strike_increase_in_profit, roll_strike_trail_profit, roll_strike_trail_profit_sign,
                                simple_momentum_range_breakout, simple_momentum, simple_momentum_sign, simple_momentum_direction,
                                range_breakout,createdBy
                            ) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
            
                values = (
                                portfolio_strategy_variable_id,  #
                                leg_value.get('lots'),
                                leg_value.get('position'),
                                leg_value.get('option_type'),
                                leg_value.get('expiry'),
                                leg_value.get('no_of_reentry'),
                                leg_value.get('strike_selection_criteria'),
                                leg_value.get('closest_premium'),
                                leg_value.get('strike_type'),
                                leg_value.get('straddle_width_value'),
                                leg_value.get('straddle_width_sign'),
                                leg_value.get('percent_of_atm_strike_value'),
                                leg_value.get('percent_of_atm_strike_sign'),
                                leg_value.get('atm_straddle_premium'),
                                leg_value.get('strike_selection_criteria_stop_loss'),
                                leg_value.get('strike_selection_criteria_stop_loss_sign'),
                                leg_value.get('strike_selection_criteria_trailing_options'),
                                leg_value.get('strike_selection_criteria_profit_reaches'),
                                leg_value.get('strike_selection_criteria_lock_profit'),
                                leg_value.get('strike_selection_criteria_lock_profit_sign'),
                                leg_value.get('strike_selection_criteria_increase_in_profit'),
                                leg_value.get('strike_selection_criteria_trail_profit'),
                                leg_value.get('strike_selection_criteria_trail_profit_sign'),
                                leg_value.get('roll_strike'),
                                leg_value.get('roll_strike_strike_type'),
                                leg_value.get('roll_strike_stop_loss'),
                                leg_value.get('roll_strike_stop_loss_sign'),
                                leg_value.get('roll_strike_trailing_options'),
                                leg_value.get('roll_strike_profit_reaches'),
                                leg_value.get('roll_strike_lock_profit'),
                                leg_value.get('roll_strike_lock_profit_sign'),
                                leg_value.get('roll_strike_increase_in_profit'),
                                leg_value.get('roll_strike_trail_profit'),
                                leg_value.get('roll_strike_trail_profit_sign'),
                                leg_value.get('simple_momentum_range_breakout'),
                                leg_value.get('simple_momentum'),
                                leg_value.get('simple_momentum_sign'),
                                leg_value.get('simple_momentum_direction'),
                                leg_value.get('range_breakout'),
                                leg_value.get('createdBy')
                            )
                        
                mycursor.execute(query, values)
                mydb.commit()
                print("Insertion successful into portfoliostrategyvariableslegs table!")
                last_id = mycursor.lastrowid  # Get the inserted portfolio_strategy_id
                print("Portfolio Strategy variable leg ID:", last_id)
                
        #Delete the legs which are not in the update legs       
        #print("Remaining legids" ,leg_ids)
        #if leg_ids:
            #placeholders = ', '.join(['%s'] * len(leg_ids))
            #query = f"DELETE FROM portfoliostrategyvariableslegs WHERE id IN ({placeholders})"
            #mycursor.execute(query, tuple(leg_ids))
            #mydb.commit()
            #print("Delete successful in portfoliostrategyvariableslegs table!")
            
    
        
    def deletestrategies(self,my_list,portId):
        mycursor = mydb.cursor()
        for value in my_list:
            query = "Delete from portfoliostrategies where portfolio_id=%s and strategy_id=%s"
            mycursor.execute(query, (portId,value,))
            print("Data deeleted from portfoliostrategies where strategy id =" + str(value))
            mydb.commit()
    
    def deleteLegs(self,my_list,portId):
        mycursor = mydb.cursor()
        for value in my_list:
            query = "Delete from portfoliostrategyvariableslegs where portfolio_strategy_variables_id=%s and id=%s"
            mycursor.execute(query, (portId,value,))
            print("Data deeleted from portfoliostrategies where strategy id =" + str(value))
            mydb.commit()
    
    def get_Strategy_ids(self,portId):
        mycursor = mydb.cursor() 
        json_id = []
        query = "SELECT strategy_id from portfoliostrategies WHERE portfolio_id=%s"
        mycursor.execute(query, (portId,))
        result = mycursor.fetchall()
        table_ids = [row[0] for row in result]
        return table_ids
    
    def get_Leg_ids(self,portId):
        mycursor = mydb.cursor() 
        json_id = []
        query = "SELECT id from portfoliostrategyvariableslegs WHERE portfolio_strategy_variables_id=%s"
        mycursor.execute(query, (portId,))
        result = mycursor.fetchall()
        table_ids = [row[0] for row in result]
        return table_ids


    def insert_data(self,portfolio,strategies,strategyvariables,legs):
        mycursor = mydb.cursor()
        print(portfolio)
        query = "SELECT id FROM portfolio WHERE name = %s"
        mycursor.execute(query, (portfolio.name,))
        result = mycursor.fetchone()
    
        if result:
            # Portfolio exists, use existing portfolio ID
            portfolio_id = result[0]
            print("Portfolio already exists. Using Portfolio ID:", portfolio_id)
            insert_strategy(strategies,strategyvariables,legs,portfolio_id)
        else:
            # Insert into portfolio table 
            mycursor.execute("SHOW COLUMNS FROM portfolio")

            # Fetch all results from the query
            columns = mycursor.fetchall()

            # Print the column information
            print("Columns in 'portfolio' table:")
            for column in columns:
                print(column)

            query = """
            INSERT INTO portfolio (name, createdBy)
            VALUES (%s, %s)
            """
            portfolio_data = (portfolio.name, portfolio.createdBy,)
            
            try:
                mycursor.execute(query, portfolio_data)
                mydb.commit()
                print("Data inserted successfully in portfolio table.")
                portfolio_id = mycursor.lastrowid
                print("Portfolio ID:", portfolio_id)
                insert_strategy(strategies, strategyvariables, legs, portfolio_id)
            except Exception as e:
                print("Error inserting into portfolio table:", e)
        # Insert into portfolio tab

        mycursor.close()
     
    #def update_data(self,portfolio,strategies,strategyvariables,legs,portId):

        

      #Update Portofloio
      #update_portfolio(portfolio,portId)
      

      #update_Strategy(strategies,portId)
      
    
    def getAllPortfolio(self):
        try:
            #mycursor = mydb.cursor(dictionary=True)
            connection = mysql.connector.connect(
            **DB_CONNECTION_PARAMS
            )

            if connection.is_connected():
                mycursor = connection.cursor(dictionary=True)
                
                value=2
                # Step 1: Fetch all unique strategy IDs
                mycursor.execute("SELECT DISTINCT id FROM portfolio")
                portfolio_ids = [row['id'] for row in mycursor.fetchall()]
                
                # List to store all strategy details
                all_portfolios = []
                
                # Step 2: Iterate over each strategy_id and fetch details
                for portfolio_id in portfolio_ids:
                    # Fetch strategy details
                    query = """
                    SELECT *
                    FROM portfolio
                    WHERE id = %s
                    """
                    mycursor.execute(query, (portfolio_id,))
                    result = mycursor.fetchall()
                    
                    # Convert to JSON format
                    strategy_details = convert_to_json(result, portfolio_id,value)
                    # Append strategy details to all_strategies list
                    #return strategy_details
                    
                    all_portfolios.extend(strategy_details)
                    #all_strategies.append(result)
                
                # Return all strategies as JSON data
                transformed_data = {"portfolio": all_portfolios}
                # Outputting the transformed data
                #print(json.dumps(transformed_data, indent=2))
                return all_portfolios
        
        except Exception as e:
            print(f"Error retrieving strategy details: {e}")
            return {"error": str(e)}
   

    def getPortfolioDetails(self, strategy_id):
        try:
        #print('3')
            value=1
            #mycursor = mydb.cursor(dictionary=True)
    
            connection = mysql.connector.connect(
               **DB_CONNECTION_PARAMS
            )
        
            if connection.is_connected():
                mycursor = connection.cursor(dictionary=True)
    
                stategy_details = ""
                query =  """
                SELECT *
                FROM portfolio
                WHERE id = %s
                """
                mycursor.execute(query, (strategy_id,))
                result = mycursor.fetchall()
                #print('4')
                stategy_details = convert_to_json(result,strategy_id,value)
                #for row in result:
                 #   strategy_details.append(row)
                 
            
                return stategy_details
        except Exception as e:
            print(f"Error retrieving strategy details: {e}")
            return {"error": str(e)}

    def getstrategyvariables(self,statVarId):
        try:
            connection = mysql.connector.connect(
               **DB_CONNECTION_PARAMS
            )
            if connection.is_connected():
                mycursor = connection.cursor(dictionary=True)
    
                stategy_details = ""
                query =  """
                SELECT *
                FROM portfoliostrategyvariables
                WHERE id = %s
                """
                mycursor.execute(query, (statVarId,))
                result = mycursor.fetchall()
                #print('4')
                variable_details = convert_legs_to_json(result,statVarId)
                return variable_details
        except Exception as e:
            print(f"Error retrieving strategy details: {e}")
            return {"error": str(e)}