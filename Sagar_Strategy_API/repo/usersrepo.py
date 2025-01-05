import json
import mysql.connector
from mysql.connector import Error
import os
import sys
from fastapi import FastAPI, HTTPException, Query

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current script
    sagar_common_path = os.path.join(current_dir, "../../Sagar_common")  # Go up two levels to "OGCODE"
    if sagar_common_path not in sys.path:
        sys.path.append(sagar_common_path)
    from common_function import fetch_parameter
except ImportError as e:
    print(f"Errorfetching db details: {e}")


def connect_to_users_db() -> mysql.connector.connection.MySQLConnection:
    try:
        env = "dev"  # Environment, e.g., 'dev', 'prod'
        key = "db_sagar_strategy"  # Example key
        db_Value = fetch_parameter(env, key)
        if db_Value is None:
            raise HTTPException(status_code=500, detail="Failed to fetch database configuration.")
        print(f"Fetched db config: {db_Value}")

        conn = mysql.connector.connect(
            host=db_Value['host'],
            database=db_Value['database'],
            user=db_Value['user'],
            password=db_Value['password'],
        )
        if conn.is_connected():
            print("Connected to database.")
            return conn
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

def convert_boolean(value):
    if isinstance(value, bool):
        return int(value)
        
    if isinstance(value, str) and value.lower() == 'true':
        return 1
    elif isinstance(value, str) and value.lower() == 'false':
        return 0
    return value



class UsersRepo:
    def __init__(self,data):
        self.data = data

    def registerUser(self,data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        #print(data)
        mycursor = conn.cursor()
        query = """
        INSERT INTO user (
            username, password, email, emailVerificationStatus, first_name, middle_name, last_name,
            mobile, mobileVerificationStatus, address, dateofbirth, risk_profile, last_login, is_active,createdBy
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """

        print(f"mobileverify {data.get('mobileVerificationStatus')}")

        values = (
        data['username'], data['password'], data['email'],
        convert_boolean(data.get('emailVerificationStatus', False)),
        data.get('first_name', ''), data.get('middle_name', ''), data.get('last_name', ''),
        data.get('mobile', ''), convert_boolean(data.get('mobileVerificationStatus', False)),
        data.get('address', ''), data.get('dateofbirth', ''), data.get('risk_profile', ''),
        data.get('last_login'), convert_boolean(data.get('is_active', True)),data.get('createdBy',1)
        )

        
        try:
            mycursor.execute(query, values)
            conn.commit()
            
            print("Record inserted successfully.")
            user_id = mycursor.lastrowid
            return user_id

        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message} 
        
        finally:
            if conn.is_connected():
                mycursor.close()
    
    def edituser(self,data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        mycursor = conn.cursor()
        check_query = "SELECT * FROM user WHERE id = %s"
        mycursor.execute(check_query, (data['id'],))
        result = mycursor.fetchone()
        if result:
        # Prepare the update query
            update_query = """
                UPDATE user
                SET 
                    username = %s,
                    password = %s,
                    email = %s,
                    emailVerificationStatus = %s,
                    first_name = %s,
                    middle_name = %s,
                    last_name = %s,
                    mobile = %s,
                    mobileVerificationStatus = %s,
                    address = %s,
                    dateofbirth = %s,
                    risk_profile = %s,
                    last_login = %s,
                    is_active = %s,
                    modifiedBy=%s
                WHERE id = %s
            """
            values = (
                data['username'],
                data['password'],
                data['email'],
                convert_boolean(data.get('emailVerificationStatus', False)),
                data['first_name'],
                data['middle_name'],
                data['last_name'],
                data['mobile'],
                convert_boolean(data.get('mobileVerificationStatus', False)),
                data['address'],
                data['dateofbirth'],
                data['risk_profile'],
                data['last_login'],
                convert_boolean(data.get('is_active', True)),
                data.get('modifiedBy',1),
                data['id']
            )
            
            try:
                mycursor.execute(update_query, values)
                conn.commit()  # Commit the changes
                return {'id': data['id'], 'update_status': True}
            except Exception as e:
                conn.rollback()  # Rollback in case of error
                return {'id': data['id'], 'update_status': False, 'error': str(e)}
        else:
            return {'id': data['id'], 'update_status': False, 'error': 'User ID not found.'}

        # Close the cursor
        mycursor.close()

    def addUserBroker(self,data):
        #print(data)
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        mycursor = conn.cursor()
        query = """
        INSERT INTO UserBrokers (
            user_id, broker_id, API_Key, API_Secret,market_api_key,market_api_secret,createdBy
        ) VALUES (%s, %s, %s, %s, %s, %s,%s)
        """
        values = (
            data['user_id'], data['broker_id'], data['api_key'], data['api_secret'],data['market_api_key'],data['market_api_secret'],data.get('createdBy',1)
        )
        
        try:
            mycursor.execute(query, values)
            conn.commit()
            
            print("Record inserted successfully.")
            user_id = mycursor.lastrowid
            return user_id

        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message} 
        
        finally:
            if conn.is_connected():
                mycursor.close()

    def editUserBroker(self,data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        mycursor = conn.cursor()
        check_query = "SELECT * FROM UserBrokers WHERE id = %s AND user_id = %s AND broker_id = %s"
        values = (data['id'],data['user_id'], data['broker_id'])
        mycursor.execute(check_query, values)
        result = mycursor.fetchone()
        if result:
        # Prepare the update query
            update_query = """
                UPDATE UserBrokers
                SET 
                    API_Key = %s,
                    API_Secret = %s,
                    market_api_key = %s,
                    market_api_secret = %s,
                    modifiedBy = %s
                WHERE id = %s AND user_id = %s AND broker_id = %s
            """
            values = (
                data['api_key'],
                data['api_secret'],
                data['market_api_key'],
                data['market_api_secret'],
                data.get('modifiedBy',1),
                data['id'],
                data['user_id'],
                data['broker_id']
            )
            
            try:
                mycursor.execute(update_query, values)
                conn.commit()  # Commit the changes
                return {'id': data['id'],'user_id': data['user_id'], 'broker_id': data['broker_id'], 'update_status': True}
            except Exception as e:
                conn.rollback()  # Rollback in case of error
                return {'id': data['id'],'user_id': data['user_id'], 'broker_id': data['broker_id'], 'update_status': False, 'error': str(e)}
        else:
            return {'id': data['id'],'user_id': data['user_id'], 'broker_id': data['broker_id'], 'update_status': False, 'error': 'UserBroker record not found.'}
            # Close the cursor
            mycursor.close()
    
    def deleteUserBroker(self,data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        mycursor = conn.cursor()
        check_query = "SELECT * FROM UserBrokers WHERE id=%s AND user_id = %s AND broker_id = %s"
        values = (data['id'],data['user_id'], data['broker_id'])
        mycursor.execute(check_query, values)
        result = mycursor.fetchone()
        if result:
            delete_query = "DELETE FROM UserBrokers WHERE id=%s AND user_id = %s AND broker_id = %s"
            try:
                mycursor.execute(delete_query, values)
                conn.commit()  # Commit the changes
                return {'id': data['id'],'user_id': data['user_id'], 'broker_id': data['broker_id'], 'delete_status': True}
            except Exception as e:
                conn.rollback()
                return {'id': data['id'],'user_id': data['user_id'], 'broker_id': data['broker_id'], 'delete_status': False, 'error': str(e)}
        else:
            return {'id': data['id'],'user_id': data['user_id'], 'broker_id': data['broker_id'], 'delete_status': False, 'error': 'UserBroker record not found.'}
            # Close the cursor
            mycursor.close()  
    
    def getAllBrokers(self):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        mycursor = conn.cursor()
        query = """SELECT id, name, createdBy, createdDate,modifiedBy,lastUpdatedDateTime FROM Broker"""
        
        try:
            mycursor.execute(query)  # Execute the query without needing 'values'
            
            # Fetch all rows from the result set
            result = mycursor.fetchall()
            
            # Format the result as a list of dictionaries
            modules = [{"id": str(row[0]), "name": row[1], "createdBy":str(row[2]),"createdDate":row[3],"modifiedBy":str(row[4]),"lastUpdatedDateTime":row[5]} for row in result]
            
            return modules  # Return the formatted result
        
        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message}
        
        finally:
            if conn.is_connected():
                mycursor.close()

    def addBroker(self,data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        #print(data)
        mycursor = conn.cursor()
        query = """
        INSERT INTO broker (
            name,createdBy
        ) VALUES (%s,%s)
        """
        values = (
            data['name'],
            data.get('createdBy',1)
        )
        
        try:
            mycursor.execute(query, values)
            conn.commit()
            
            # Fetch the inserted broker's ID (assuming it is auto-incremented)
            user_id = mycursor.lastrowid  # This will get the last inserted row's ID
            
            print(f"Record inserted successfully with ID: {user_id}")
            return {"id": user_id}  # Return the ID in a dictionary

        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message} 
        
        finally:
            if conn.is_connected():
                mycursor.close()

    def editBroker(self,data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        mycursor = conn.cursor()
        check_query = "SELECT * FROM broker WHERE id = %s"
        values = (data['id'],)
        mycursor.execute(check_query, values)
        result = mycursor.fetchone()
        if result:
        # Prepare the update query
            update_query = """
                UPDATE broker
                SET 
                    name = %s,
                    modifiedBy = %s
                WHERE id = %s
            """
            values = (
                data['name'],
                data.get('modifiedBy',1),
                data['id']
            )
            
            try:
                mycursor.execute(update_query, values)
                conn.commit()  # Commit the changes
                return {'id': data['id'], 'update_status': True}
            except Exception as e:
                conn.rollback()  # Rollback in case of error
                return {'id': data['id'], 'update_status': False, 'error': str(e)}
        else:
            return {'id': data['id'], 'update_status': False, 'error': 'UserBroker record not found.'}
            # Close the cursor
            mycursor.close()
    
    def deleteBroker(self,data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        mycursor = conn.cursor()
        check_query = "SELECT * FROM broker WHERE id = %s"
        values = (data['id'],)
        mycursor.execute(check_query, values)
        result = mycursor.fetchone()
        if result:
            delete_query = "DELETE FROM broker WHERE id = %s"
            try:
                mycursor.execute(delete_query, values)
                conn.commit()  # Commit the changes
                return {'id': data['id'],'delete_status': True}
            except Exception as e:
                conn.rollback()
                return {'id': data['id'],'delete_status': False, 'error': str(e)}
        else:
            return {'id': data['id'],'delete_status': False, 'error': 'UserBroker record not found.'}
            # Close the cursor
            mycursor.close()  

    def addBilling(self, data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
    # Create cursor to execute SQL queries
        mycursor = conn.cursor()

        # Initialize the list of columns and values to be inserted
        columns = ["user_id", "billing_type", "createdBy"]
        values = [data['user_id'], data['billing_type'], data.get('createdBy',1)]

        # Add profit_sharing_type only if not already in the list (based on billing_type)
        if data['billing_type'] == 'profit sharing':
            columns.append("profit_sharing_type")
            values.append(data['profit_sharing_type'])

        # Add one_time_fee based on billing_type condition
        if data['billing_type'] == 'one time':
            columns.append("one_time_fee")
            values.append(data.get('one_time_fee', 0))  # Default to 0 if not provided
        else:
            # Set one_time_fee to 0 if not 'one time'
            columns.append("one_time_fee")
            values.append(0)

        # If the billing_type is 'subscription', include subscription_type and subscription_fee
        if data['billing_type'] == 'subscription':
            columns.extend(["subscription_type", "subscription_fee"])
            values.extend([data.get('subscription_type'), data.get('subscription_fee') or None])  # Default to None if empty
        else:
            # Set subscription_type and subscription_fee to None for other billing types
            columns.extend(["subscription_type", "subscription_fee"])
            values.extend([None, None])

        # If the profit_sharing_type is 'flat', include profit_sharing_flat_profit_percent and profit_sharing_flat_less_percent
        if data.get('profit_sharing_type') == 'flat' and data.get('billing_type') == 'profit sharing':
            columns.extend(["profit_sharing_flat_profit_percent", "profit_sharing_flat_less_percent"])
            values.extend([data.get('profit_sharing_flat_profit_percent') or None, 
                        data.get('profit_sharing_flat_less_percent') or None])
        else:
            # Set profit sharing flat percentages to None if profit_sharing_type is not 'flat'
            columns.extend(["profit_sharing_flat_profit_percent", "profit_sharing_flat_less_percent"])
            values.extend([None, None])

        # Construct the SQL query dynamically based on columns and values
        query = f"""
        INSERT INTO billing ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(values))})
        """

        try:
            # Execute the query with the provided values
            mycursor.execute(query, values)

            # Commit the transaction to save the data
            conn.commit()

            # Get the ID of the last inserted row
            billing_id = mycursor.lastrowid
            print(f"Record inserted successfully with ID: {billing_id}")

            # If the profit_sharing_type is 'slab', insert into ProfitSharingSlabs
            if data.get('profit_sharing_type') == 'slab' and data.get('billing_type') == 'profit sharing':
                for slab in data['profit_sharing_slabs']:
                    slab_query = """
                        INSERT INTO ProfitSharingSlabs (billing_id, `from`, `to`, profit_percent, less_percent,createdBy)
                        VALUES (%s, %s, %s, %s, %s,%s)
                    """
                    slab_values = (
                        billing_id,
                        slab['from'],
                        slab['to'],
                        slab['profit_percent'],
                        slab['less_percent'],
                        slab.get('createdBy',1)
                    )
                    mycursor.execute(slab_query, slab_values)

                # Commit the transaction to save the slabs data
                conn.commit()

            return billing_id

        except Error as e:
            # Handle any errors during execution
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message}

        finally:
            # Ensure the cursor is closed after execution
            if conn.is_connected():
                mycursor.close()

    def editBilling(self, data):
        conn = connect_to_users_db()
        billing_id = data['id']
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        mycursor = conn.cursor()

        # Prepare the columns and values to be updated
        columns = ["user_id", "billing_type", "modifiedBy"]
        values = [data['user_id'], data['billing_type'], data.get('modifiedBy', 1)]

        # Add profit_sharing_type if it exists in the request data
        if data.get('billing_type') == 'profit sharing':
            columns.append("profit_sharing_type")
            values.append(data['profit_sharing_type'])

        # Add one_time_fee based on billing_type condition
        if data['billing_type'] == 'one time':
            columns.append("one_time_fee")
            values.append(data.get('one_time_fee', 0))  # Default to 0 if not provided
        else:
            # Set one_time_fee to 0 if not 'one time'
            columns.append("one_time_fee")
            values.append(0)

        # If the billing_type is 'subscription', include subscription_type and subscription_fee
        if data['billing_type'] == 'subscription':
            columns.extend(["subscription_type", "subscription_fee"])
            values.extend([data.get('subscription_type'), data.get('subscription_fee') or None])  # Default to None if empty
        else:
            # Set subscription_type and subscription_fee to None for other billing types
            columns.extend(["subscription_type", "subscription_fee"])
            values.extend([None, None])

        # If the profit_sharing_type is 'flat', include profit_sharing_flat_profit_percent and profit_sharing_flat_less_percent
        if data.get('profit_sharing_type') == 'flat' and data.get('billing_type') == 'profit sharing':
            columns.extend(["profit_sharing_flat_profit_percent", "profit_sharing_flat_less_percent"])
            values.extend([data.get('profit_sharing_flat_profit_percent') or None, 
                        data.get('profit_sharing_flat_less_percent') or None])
        else:
            # Set profit sharing flat percentages to None if profit_sharing_type is not 'flat'
            columns.extend(["profit_sharing_flat_profit_percent", "profit_sharing_flat_less_percent"])
            values.extend([None, None])

        # Construct the SQL query dynamically based on columns and values
        set_query = ", ".join([f"{col} = %s" for col in columns])
        update_query = f"""
        UPDATE billing
        SET {set_query}
        WHERE id = %s
        """
        values.append(billing_id)

        try:
            # Execute the update query with the provided values
            mycursor.execute(update_query, values)
            
            # Check if we need to delete profit sharing slabs
            # If the profit_sharing_type is 'slab', insert into ProfitSharingSlabs
            if data.get('profit_sharing_type') == 'slab' and data.get('billing_type') == 'profit sharing':
                # First, delete the existing slabs for this billing_id
                delete_slab_query = """
                    DELETE FROM ProfitSharingSlabs 
                    WHERE billing_id = %s
                """
                mycursor.execute(delete_slab_query, (billing_id,))
                
                # Now, insert the new slabs provided in the request
                for slab in data['profit_sharing_slabs']:
                    slab_query = """
                        INSERT INTO ProfitSharingSlabs (billing_id, `from`, `to`, profit_percent, less_percent, createdBy)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    slab_values = (
                        billing_id,
                        slab['from'],
                        slab['to'],
                        slab['profit_percent'],
                        slab['less_percent'],
                        slab.get('createdBy', 1)
                    )
                    mycursor.execute(slab_query, slab_values)
            
            elif data.get('profit_sharing_type') != 'slab' and data.get('billing_type') == 'profit sharing':
                # If 'profit_sharing_type' is changed and is no longer 'slab', delete related slabs
                delete_slab_query = """
                    DELETE FROM ProfitSharingSlabs 
                    WHERE billing_id = %s
                """
                mycursor.execute(delete_slab_query, (billing_id,))

            # Commit the transaction to save the updated data
            conn.commit()

            return data

        except Error as e:
            # Handle any errors during execution
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message}

        finally:
            # Ensure the cursor is closed after execution
            if conn.is_connected():
                mycursor.close()
                conn.close()


    def getAllModules(self):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        mycursor = conn.cursor()
        query = """SELECT id, name,createdBy, createdDate,modifiedBy,lastUpdatedDateTime FROM Modules"""
        
        try:
            mycursor.execute(query)  # Execute the query without needing 'values'
            
            # Fetch all rows from the result set
            result = mycursor.fetchall()
            
            # Format the result as a list of dictionaries
            modules = [{"id": str(row[0]), "name": row[1], "createdBy":str(row[2]),"createdDate":row[3],"modifiedBy":str(row[4]),"lastUpdatedDateTime":row[5]} for row in result]
            
            return modules  # Return the formatted result
        
        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message}
        
        finally:
            if conn.is_connected():
                mycursor.close()

    def addModules(self,data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        #print(data)
        mycursor = conn.cursor()
        query = """
        INSERT INTO Modules (
            name,createdBy
        ) VALUES (%s,%s)
        """
        values = (
            data['name'],data.get('createdBy',1),
        )
        
        try:
            mycursor.execute(query, values)
            conn.commit()
            
            # Fetch the inserted broker's ID (assuming it is auto-incremented)
            user_id = mycursor.lastrowid  # This will get the last inserted row's ID
            
            print(f"Record inserted successfully with ID: {user_id}")
            return {"id": user_id}  # Return the ID in a dictionary

        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message} 
        
        finally:
            if conn.is_connected():
                mycursor.close()

    def addUserAccessModules(self, data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        mycursor = conn.cursor()
        
        query = """
        INSERT INTO UserAccessModules (
            user_id, module_id, enabled,createdBy
        ) VALUES (%s, %s, %s, %s)
        """
        
        inserted_data = []  # This will hold the results to return
        
        try:
            for entry in data:
                # Insert data
                values = (entry['user_id'], entry['module_id'], entry['enabled'],entry.get('createdBy',1))
                mycursor.execute(query, values)
                
                # After executing the insert, fetch the generated ID for the current row
                inserted_id = mycursor.lastrowid
                
                # Append the inserted record with the generated ID
                inserted_data.append({
                    'id': inserted_id,
                    'user_id': entry['user_id'],
                    'module_id': entry['module_id'],
                    'enabled': entry['enabled'],
                    'createdBy':entry.get('createdBy',1)
                })
            
            # Commit the transaction after all inserts
            conn.commit()
            
            print("Records inserted successfully.")
            
            return inserted_data  # Return the data with the new IDs
            
        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message}
        
        finally:
            if conn.is_connected():
                mycursor.close()
    
    def editUserAccessModules(self,data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        mycursor = conn.cursor()
        check_query = "SELECT * FROM UserAccessModules WHERE id = %s"
        mycursor.execute(check_query, (data['id'],))
        result = mycursor.fetchone()
        if result:
        # Prepare the update query
            update_query = """
                UPDATE UserAccessModules
                SET 
                    user_id = %s,
                    module_id = %s,
                    enabled = %s,
                    modifiedBy=%s
                WHERE id = %s
            """
            values = (
                data['user_id'],
                data['module_id'],
                data['enabled'],
                data.get('modifiedBy',1),
                data['id']
            )
            
            try:
                mycursor.execute(update_query, values)
                conn.commit()  # Commit the changes
                return {'id': data['id'], 'update_status': True}
            except Exception as e:
                conn.rollback()  # Rollback in case of error
                return {'id': data['id'], 'update_status': False, 'error': str(e)}
        else:
            return {'id': data['id'], 'update_status': False, 'error': 'ID not found.'}

        # Close the cursor
        mycursor.close()

    def getAllUsers(self):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        mycursor = conn.cursor()
        query = """SELECT id, username, password, email, emailVerificationStatus, 
                          first_name, middle_name, last_name, mobile, mobileVerificationStatus, 
                          address, dateofbirth, risk_profile, last_login, is_active ,
                          createdBy, createdDate,modifiedBy,lastUpdatedDateTime
                   FROM User"""
        
        try:
            mycursor.execute(query)  # Execute the query without needing 'values'
            
            # Fetch all rows from the result set
            result = mycursor.fetchall()
            
            # Format the result as a list of dictionaries
            users = [{
                "id": str(row[0]), 
                "username": row[1], 
                "password": row[2], 
                "email": row[3], 
                "emailVerificationStatus": row[4],
                "first_name": row[5], 
                "middle_name": row[6], 
                "last_name": row[7], 
                "mobile": row[8], 
                "mobileVerificationStatus": row[9], 
                "address": row[10], 
                "dateofbirth": row[11], 
                "risk_profile": row[12], 
                "last_login": row[13], 
                "is_active": row[14],
                "createdBy":str(row[15]),
                "createdDate":row[16],
                "modifiedBy":str(row[17]),
                "lastUpdatedDateTime":row[18]
            } for row in result]
            
            return users  # This return should be inside the method
        
        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message}
        
        finally:
            if conn.is_connected():
                mycursor.close()
                conn.close()
    
    def getUser(self, data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        mycursor = conn.cursor()
        query = """SELECT id, username, password, email, emailVerificationStatus, 
                          first_name, middle_name, last_name, mobile, mobileVerificationStatus, 
                          address, dateofbirth, risk_profile, last_login, is_active,
                          createdBy, createdDate, modifiedBy, lastUpdatedDateTime
                   FROM User WHERE id = %s"""

        try:
            user_id = self.data["id"]  # Ensure 'id' is extracted correctly
            mycursor.execute(query, (user_id,))  # Pass the user_id as a parameter

            # Fetch one row from the result set
            row = mycursor.fetchone()

            if row:
                # Format the result as a dictionary
                user = {
                    "id": str(row[0]), 
                    "username": row[1], 
                    "password": row[2], 
                    "email": row[3], 
                    "emailVerificationStatus": row[4],
                    "first_name": row[5], 
                    "middle_name": row[6], 
                    "last_name": row[7], 
                    "mobile": row[8], 
                    "mobileVerificationStatus": row[9], 
                    "address": row[10], 
                    "dateofbirth": row[11], 
                    "risk_profile": row[12], 
                    "last_login": row[13], 
                    "is_active": row[14],
                    "createdBy": str(row[15]),
                    "createdDate": row[16],
                    "modifiedBy": str(row[17]),
                    "lastUpdatedDateTime": row[18]
                }
                return user
            else:
                raise HTTPException(status_code=404, detail="User not found")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

        finally:
            if conn.is_connected():
                mycursor.close()
                conn.close()

    def getBilling(self, data):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        mycursor = conn.cursor()
        query = """SELECT id, user_id, billing_type, one_time_fee, subscription_type, subscription_fee, 
                        profit_sharing_type, profit_sharing_flat_profit_percent, profit_sharing_flat_less_percent, 
                        createdBy, createdDate, modifiedBy, lastUpdatedDateTime
                FROM Billing 
                WHERE user_id = %s"""
        
        try:
            user_id = data["user_id"]  # Correctly using 'data' to get the user_id
            mycursor.execute(query, (user_id,))
            
            # Fetch all rows from the result set
            result = mycursor.fetchall()
            
            users = []  # Initialize an empty list for formatted result
            
            for row in result:
                # Format the billing data
                billing_data = {
                    "id": str(row[0]), 
                    "user_id": row[1], 
                    "billing_type": row[2], 
                    "one_time_fee": row[3], 
                    "subscription_type": row[4],
                    "subscription_fee": row[5], 
                    "profit_sharing_type": row[6],
                    "profit_sharing_flat_profit_percent": row[7],
                    "profit_sharing_flat_less_percent": row[8],
                    "createdBy": str(row[9]),
                    "createdDate": row[10],
                    "modifiedBy": str(row[11]),
                    "lastUpdatedDateTime": row[12]
                }
                
                # Fetch the profit sharing slabs if the condition matches
                if row[6] == 'slab' and row[2] == 'profit sharing':  # profit_sharing_type == 'slab' and billing_type == 'profit sharing'
                    slabs_query = """SELECT id,billing_id,`from`, `to`, profit_percent, less_percent, createdBy,createdDate, modifiedBy, lastUpdatedDateTime
                                    FROM ProfitSharingSlabs 
                                    WHERE billing_id = %s"""
                    mycursor.execute(slabs_query, (row[0],))  # row[0] is the billing_id (id)
                    slabs_result = mycursor.fetchall()
                    
                    # Format the profit sharing slabs data
                    slabs = [{
                        "id": slab[0],
                        "billing_id": slab[1],
                        "from": slab[2],
                        "to": slab[3],
                        "profit_percent": slab[4],
                        "less_percent": slab[5],
                        "createdBy": slab[6],
                        "createdDate": slab[7],
                        "modifiedBy": slab[8],
                        "lastUpdatedDateTime": slab[9]
                    } for slab in slabs_result]
                    
                    # Add the slabs data to the billing data
                    billing_data["profit_sharing_slabs"] = slabs
                
                # Add the formatted billing data to the list
                users.append(billing_data)
            
            return users  # Return the list of users with billing data and slabs

        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message}
        
        finally:
            if conn.is_connected():
                mycursor.close()
                conn.close()

    def getUserAccessModules(self,data):
        conn = connect_to_users_db()
        print(f"user id is {self.data["user_id"]}")
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        mycursor = conn.cursor()
        query = """SELECT id,user_id, module_id, enabled, createdBy, createdDate,modifiedBy,lastUpdatedDateTime
                   FROM useraccessmodules WHERE user_id = %s"""
        
        try:
            user_id = self.data["user_id"]  # Ensure 'id' is extracted correctly
            mycursor.execute(query, (user_id,))
  # Execute the query without needing 'values'
            
            # Fetch all rows from the result set
            result = mycursor.fetchall()
            
            # Format the result as a list of dictionaries
            users = [{
                "id": str(row[0]), 
                "user_id": row[1], 
                "module_id": row[2], 
                "enabled": bool(row[3]),
                "createdBy":str(row[4]),
                "createdDate":row[5],
                "modifiedBy":str(row[6]),
                "lastUpdatedDateTime":row[7]
            } for row in result]
            
            return users  # This return should be inside the method
        
        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message}
        
        finally:
            if conn.is_connected():
                mycursor.close()
                conn.close()

    def getAllUserBroker(self):
        conn = connect_to_users_db()

        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        mycursor = conn.cursor()
        query = """SELECT id,user_id, broker_id, API_Key, API_Secret, market_api_key, 
                          market_api_secret, createdBy, createdDate,modifiedBy,lastUpdatedDateTime
                   FROM UserBrokers"""
        
        try:
            mycursor.execute(query)  # Execute the query without needing 'values'
            
            # Fetch all rows from the result set
            result = mycursor.fetchall()
            
            # Format the result as a list of dictionaries
            users = [{
                "id": str(row[0]), 
                "user_id": row[1], 
                "broker_id": row[2], 
                "API_Key": row[3], 
                "API_Secret": row[4],
                "market_api_key": row[5], 
                "market_api_secret": row[6],
                "createdBy":str(row[7]),
                "createdDate":row[8],
                "modifiedBy":str(row[9]),
                "lastUpdatedDateTime":row[10]
            } for row in result]
            
            return users  # This return should be inside the method
        
        except Error as e:
            error_message = f"Error: {e}"
            print(error_message)
            return {"error": error_message}
        
        finally:
            if conn.is_connected():
                mycursor.close()
                conn.close()