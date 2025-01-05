from fastapi import FastAPI, HTTPException, Query

from pydantic import BaseModel
from typing import List, Any, Optional, Dict, Union
from fastapi.middleware.cors import CORSMiddleware
import requests
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
import json
import sys
import pandas as pd
import logging

# Adjust system path to include the project root
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Correct imports
try:
    from service.userservice import UserService
    from repo.usersrepo import UsersRepo
except ImportError as e:
    print(f"Error importing UserService: {e}")


# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
   allow_origins=[
        "http://127.0.0.1:8080",  # Include 127.0.0.1 with the specific port
        "http://localhost:3000",  # Include localhost with the specific port
    ],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# ------------------------------------------------------------------------------------------------------
# USERS APIS
# ------------------------------------------------------------------------------------------------------

# User Registration
@app.post("/registeruser", response_model=dict)
async def registeruser(data: dict):
    try:
        print(type(data))
        user_service = UserService(data)
        print(1)
        user_id = user_service.registerUser(data)
        data["id"] = user_id
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Edit User Details
@app.put("/edituser/{user_id}", response_model=dict)
async def edituser(user_id: int, data: dict):
    try:
        print(f"Editing user with ID: {user_id}")
        data['id'] = user_id  # Assign the user_id from the URL to the data
        user_service = UserService(data)
        user_id = user_service.edituser(data)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Add UserBroker
@app.post("/addUserBroker", response_model=dict)
async def addUserBroker(data: dict):
    try:
        print(type(data))
        user_service = UserService(data)
        value = user_service.addUserBroker(data)
        data = {"id": value} | data
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Edit User Broker
@app.post("/editUserBroker/{user_id}", response_model=dict)
async def editUserBroker(user_id: int, data: dict):

    try:
        print(f"Editing user with ID: {user_id}")
        data['id'] = user_id  # Assign the user_id from the URL to the data
        user_service = UserService(data)
        user_id = user_service.editUserBroker(data)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Delete User Broker
@app.post("/deleteUserBroker/{user_id}", response_model=dict)
async def deleteUserBroker(user_id: int, data: dict):
    
    try:
        print(f"Editing user with ID: {user_id}")
        data['id'] = user_id  # Assign the user_id from the URL to the data
        user_service = UserService(data)
        user_id = user_service.deleteUserBroker(data)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Add Broker
@app.post("/addBroker", response_model=dict)
async def addBroker(data: dict):

    try:
        print(type(data))
        #print(data)
        user_service = UserService(data)
        user_id = user_service.addBroker(data)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Edit Broker
@app.put("/editBroker/{user_id}", response_model=dict)
async def editBroker(user_id: int, data: dict):
    try:
        print(f"Editing user with ID: {user_id}")
        data['id'] = user_id  # Assign the user_id from the URL to the data
        user_service = UserService(data)
        user_id = user_service.editBroker(data)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Delete Broker
@app.post("/deleteBroker/{user_id}", response_model=dict)
async def deleteBroker(user_id: int, data: dict):
    
    try:
        print(f"Editing user with ID: {user_id}")
        data['id'] = user_id  # Assign the user_id from the URL to the data
        user_service = UserService(data)
        user_id = user_service.deleteBroker(data)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#GET ALL Brokers
@app.get("/getAllBrokers", response_model=list)
async def getAllBrokers():

    try:
        data = []
        user_service = UserService(data)
        value = user_service.getAllBrokers(data)
        return value

    except Exception as e:
        # Handle unexpected exceptions and provide error response
        raise HTTPException(status_code=500, detail=str(e))


#Add Billing
@app.post("/addBilling", response_model=dict)
async def addBilling(data: dict):
    
    try:
        print(type(data))
        print(data)
        user_service = UserService(data)
        user_id = user_service.addBilling(data)
        data = {"id": user_id} | data
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Edit Billing
@app.put("/editBilling/{user_id}", response_model=dict)
async def editBilling(user_id: int, data: dict):

    try:
        print(f"Editing user with ID: {user_id}")
        data['id'] = user_id  # Assign the user_id from the URL to the data
        user_service = UserService(data)
        user_id = user_service.editBilling(data)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Add Modules
@app.post("/addModules", response_model=dict)
async def addModules(data: dict):

    try:
        print(type(data))
        print(data)
        user_service = UserService(data)
        user_id = user_service.addModules(data)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#GET ALL MODULES
@app.get("/getAllModules", response_model=list)
async def getAllModules():

    try:
        data = []
        user_service = UserService(data)
        value = user_service.getAllModules(data)
        return value

    except Exception as e:
        # Handle unexpected exceptions and provide error response
        raise HTTPException(status_code=500, detail=str(e))



#Add UserAccessModules
@app.post("/addUserAccessModules", response_model=list)
async def addUserAccessModules(data: List[dict]):  

    try:
        print(type(data))  
        user_service = UserService(data)
        value = user_service.addUserAccessModules(data)  

        # Check if the value returned is True (successful operation)
        return value

    except Exception as e:
        # Handle unexpected exceptions and provide error response
        raise HTTPException(status_code=500, detail=str(e))

#Edit UserAccessModules
@app.put("/editUserAccessModules/{user_id}", response_model=dict)
async def editUserAccessModules(user_id: int, data: dict):

    try:
        print(f"Editing user with ID: {user_id}")
        data['id'] = user_id  # Assign the user_id from the URL to the data
        user_service = UserService(data)
        user_id = user_service.editUserAccessModules(data)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#GET ALL USERS
@app.get("/getAllUsers", response_model=list)
async def getAllUsers():

    try:
        data = []
        user_service = UserService(data)
        value = user_service.getAllUsers(data)
        return value

    except Exception as e:
        # Handle unexpected exceptions and provide error response
        raise HTTPException(status_code=500, detail=str(e))

#GET SINGLE USERS
@app.get("/getUser/{user_id}", response_model=dict)
async def getUser(user_id: int):
    try:
        # Pass the user_id directly to the UserService
        user_service = UserService({"id": user_id})
        user = user_service.getUser()
        return user
    except HTTPException as e:
        # Re-raise HTTPExceptions to return the correct status code
        raise e
    except Exception as e:
        # Catch other exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))

#GET Billing USERS
@app.get("/getBilling/{user_id}", response_model=list)
async def getBilling(user_id: int):
    try:
        # Pass the user_id directly to the UserService
        user_service = UserService({"user_id": user_id})
        user = user_service.getBilling()
        return user
    except HTTPException as e:
        # Re-raise HTTPExceptions to return the correct status code
        raise e
    except Exception as e:
        # Catch other exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))

#GET Billing USERS
@app.get("/getUserAccessModules/{user_id}", response_model=list)
async def getUserAccessModules(user_id: int):
    try:
        # Pass the user_id directly to the UserService
        user_service = UserService({"user_id": user_id})
        user = user_service.getUserAccessModules()
        return user
    except HTTPException as e:
        # Re-raise HTTPExceptions to return the correct status code
        raise e
    except Exception as e:
        # Catch other exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=str(e))

#GET ALL USERS
@app.get("/getAllUserBroker", response_model=list)
async def getAllUserBroker():

    try:
        data = []
        user_service = UserService(data)
        value = user_service.getAllUserBroker(data)
        return value

    except Exception as e:
        # Handle unexpected exceptions and provide error response
        raise HTTPException(status_code=500, detail=str(e))

# Main for running the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
