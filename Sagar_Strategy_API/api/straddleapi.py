import os
import json
import sys

current_directory = os.path.dirname('straddleapi.py')
# Construct the path to the parent directory
parent_directory = os.path.abspath(os.path.join(current_directory, '..'))
# Add the parent directory to the system path
sys.path.append(parent_directory)#os.chdir('D:/Rupendra/Work/Sagar/Sagar_Strategy_API')
#print(f"Changed directory to: {os.getcwd()}")
from repo.straddlerepo import StraddleRepo
from flask import Flask, request, jsonify
from flask_cors import CORS
# Change directory
#os.chdir('C:/Ajay')
#print(f"Changed directory to: {os.getcwd()}")

# Attempt to import StraddleRepo and Strategyservice
try:
    from repo.straddlerepo import StraddleRepo
except ImportError as e:
    print(f"Error importing StraddleRepo: {e}")

try:
    from service.straddleservice import Strategyservice
except ImportError as e:
    print(f"Error importing Strategyservice: {e}")
    
try:
    from repo.portfoliorepo import PortfolioRepo
except ImportError as e:
    print(f"Error importing PortfolioRepo: {e}")

try:
    from service.portfolioservice import Portfolioservice
except ImportError as e:
    print(f"Error importing Portfolioservice: {e}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

#STRATEGIES API

#Return all strategy names
@app.route('/strategies/name', methods=['GET'])
def get_strategy_name():
    try:
        data=[]
        strategy_name = []
        strategy = Strategyservice(data)
        strategy_name = strategy.getStrategyName()
        print(strategy_name)
        return jsonify(strategy_name), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Add new strategy
@app.route('/strategies', methods=['POST'])
def save_strategy():
    try:
        data = []
        data = request.get_json()
        
        transformed_data = {"strategies": data}
        # Example processing (you might want to pass this data to Strategyservice)
        #print("Received JSON data:", transformed_data)
        strategy = Strategyservice(transformed_data)
        strategy.process_insert_data(transformed_data)
        
        response = {
            "status": "success",
            "received_data": transformed_data
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Update existing strategy
@app.route('/strategies/<int:strategy_id>', methods=['PUT'])
def update_strategy(strategy_id):
    try:
        data = []
        data = request.get_json()
        print("Received JSON data:", data)
        transformed_data = {"strategies": data}
        # Example processing (you might want to pass this data to Strategyservice)
        print("Received JSON data:", transformed_data)
        # Example processing (you might want to pass this data to Strategyservice)
        strategy = Strategyservice(transformed_data)
        strategy.process_update_data(transformed_data,strategy_id)
        
        response = {
            "status": "success",
            "received_data": data
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Return single strategy
@app.route('/strategies/<int:strategy_id>', methods=['GET'])
def get_strategy_details(strategy_id):
    #print("Data from db.json:", data) 
    data =[]
    strategy_details = []
    strategy = Strategyservice(data)
    #print('1')
    strategy_details = strategy.getStrategyDetails(strategy_id)
    
    return jsonify(strategy_details), 200

#Return all strategies
@app.route('/strategies', methods=['GET'])
def get_all_strategies():
    data =[]
    strategy_details =[]
    strategy = Strategyservice(data)
    #print('1')
    strategy_details = strategy.getAllStrategyDetails()
    
    return jsonify(strategy_details), 200

#----------------------------------------------------------------------------#
#PORTFOLIO APIS
#----------------------------------------------------------------------------#

#Add new portfolio
@app.route('/portfolios', methods=['POST'])
def save_portfolios():
    try:
        data =[]
        data = request.get_json()
        #print("Received JSON data:", data)
        
        strategy = Portfolioservice(data)
        strategy.process_insert_data(data)
        
        response = {
            "status": "success",
            "received_data": data
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Update existing portfolio
@app.route('/portfolios/<int:strategyId>', methods=['PUT'])
def update_portfolio(strategyId):
    try:
        data = []
        data = request.get_json()
        print("Received JSON data:", data)
        #print(strategyId)
        # Example processing (you might want to pass this data to Strategyservice)
        strategy = Portfolioservice(data)
        strategy.process_update_data(data,strategyId)
        
        response = {
            "status": "success",
            "received_data": data
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Return All Portfolios
@app.route('/portfolios', methods=['GET'])
def get_all_portfolios():
    data =[]
    strategy_details = []
    strategy = Portfolioservice(data)
    #print('1')
    strategy_details = strategy.getAllPortfolioDetails()
    
    return jsonify(strategy_details), 200

#Return single Portfolio
@app.route('/portfolios/<int:strategy_id>', methods=['GET'])
def get_portfolio_details(strategy_id):
    #print("Data from db.json:", data) 
    data =[]
    strategy_details = []
    strategy = Portfolioservice(data)
    #print('1')
    strategy_details = strategy.getPortfolioDetails(strategy_id)
    
    return jsonify(strategy_details), 200

#Update existing strategy variables
@app.route('/strategyvariables/<int:statVarId>', methods=['PUT'])
def update_strategyvariables(statVarId):
    try:
        data = []
        data = request.get_json()
        #print("Received JSON data:", data)
        #print(strategyId)
        # Example processing (you might want to pass this data to Strategyservice)
        strategy = Portfolioservice(data)
        strategy.var_update(data,statVarId)
        #newdata = strategy.var_update(data,statVarId)
        
        response = {
            "status": "success",
            "received_data": data
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


try:
    if __name__ == '__main__':
        app.run()
except SystemExit as e:
    print("SystemExit Exception:", e)
