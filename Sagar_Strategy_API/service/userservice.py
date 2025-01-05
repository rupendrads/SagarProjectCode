import os
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
try:
    from repo.usersrepo import UsersRepo
except ImportError as e:
    print(f"Error importing Portfolioservice: {e}")
    
import json


class UserService:
    def __init__(self,data):
        self.data = data

    def registerUser(self,data):
        repo = UsersRepo(data)
        values = repo.registerUser(data)
        return values
    
    def edituser(self,data):
        repo = UsersRepo(data)
        values = repo.edituser(data)
        return values

    def addUserBroker(self,data):
        repo = UsersRepo(data)
        values = repo.addUserBroker(data)
        return values

    def editUserBroker(self,data):
        repo = UsersRepo(data)
        values = repo.editUserBroker(data)
        return values

    def deleteUserBroker(self,data):
        repo = UsersRepo(data)
        values = repo.deleteUserBroker(data)
        return values

    def addBroker(self,data):
        repo = UsersRepo(data)
        values = repo.addBroker(data)
        return values

    def editBroker(self,data):
        repo = UsersRepo(data)
        values = repo.editBroker(data)
        return values

    def deleteBroker(self,data):
        repo = UsersRepo(data)
        values = repo.deleteBroker(data)
        return values
    
    def addBilling(self,data):
        repo = UsersRepo(data)
        values = repo.addBilling(data)
        return values

    def editBilling(self,data):
        repo = UsersRepo(data)
        values = repo.editBilling(data)
        return values
    
    def getAllBrokers(self,data):
        repo = UsersRepo(data)
        values = repo.getAllBrokers()
        return values

    def addModules(self,data):
        repo = UsersRepo(data)
        values = repo.addModules(data)
        return values

    def editUserAccessModules(self,data):
        repo = UsersRepo(data)
        values = repo.editUserAccessModules(data)
        return values

    def editBilling(self,data):
        repo = UsersRepo(data)
        values = repo.editBilling(data)
        return values

    def getAllModules(self,data):
        repo = UsersRepo(data)
        values = repo.getAllModules()
        return values
    
    def getAllUsers(self,data):
        repo = UsersRepo(data)
        values = repo.getAllUsers()
        return values
    
    def getAllUserBroker(self,data):
        repo = UsersRepo(data)
        values = repo.getAllUserBroker()
        return values
    
    def getUser(self):
        repo = UsersRepo(self.data)
        values = repo.getUser(self.data)
        return values

    def getBilling(self):
        repo = UsersRepo(self.data)
        values = repo.getBilling(self.data)
        return values

    def getUserAccessModules(self):
        repo = UsersRepo(self.data)
        values = repo.getUserAccessModules(self.data)
        return values