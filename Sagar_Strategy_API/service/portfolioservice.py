
from repo.portfoliorepo import PortfolioRepo
import json


def refactor_strategy(data,port_Id):
    strategy_id = []
    for value in data:
        strategies = value.get('strategy_id',0)
        strategy_id.append(strategies)
    #print(strategy_id)
    strategy_id_list = [int(item) for item in strategy_id]
    #print(strategy_id_list)
    
    repo = PortfolioRepo()
    table_ids = repo.get_Strategy_ids(port_Id)
    #print(table_ids)
    
    SET_TABLE = set(table_ids)
    SET_JSON = set(strategy_id_list)
    
    #print(SET_TABLE)
    #print(SET_JSON)
    diff = SET_TABLE - SET_JSON
    #print(diff)
    my_list = list(diff)

    print(my_list)
    repo.deletestrategies(my_list,port_Id)
    
def refactor_legs(data,statvarId):
    leg_id = []
    for value in data:
        legs = value.get('id',0)
        leg_id.append(legs)
    leg_id_list = [int(item) for item in leg_id]
    repo = PortfolioRepo()
    table_ids = repo.get_Leg_ids(statvarId)
    
    SET_TABLE = set(table_ids)
    SET_JSON = set(leg_id_list)
    
    #print(SET_TABLE)
    #print(SET_JSON)
    diff = SET_TABLE - SET_JSON
    #print(diff)
    my_list = list(diff)

    print(my_list)
    repo.deleteLegs(my_list,statvarId)
    
    
class Portfolioservice:
    def __init__(self,data):
        self.data = data
        #self.strategyId = strategyId
    
    def process_insert_data(self, data):
        #portfolio = Portfolio(id=data['id'], name=data['name'])
        strategies = []
        strategy_variables = []
        legs = []
        #print(data)
    
        # Create Portfolio object
        portfolio = Portfolio(id=self.data.get('id'), name=self.data.get('name'),createdBy=self.data.get('createdBy',1),modifiedBy=self.data.get('modifiedBy',1))
        #print(data['strategies'])
        print(portfolio)
        # Iterate over each strategy in the data
        for strategy_data in data['strategies']: 
            #print(6)
            # Create Strategy object
            strategy = Strategy(
                id=strategy_data.get('id'),
                portfolio_id=portfolio.id,
                strategy_id=strategy_data.get('strategy_id',0),
                symbol=strategy_data.get('symbol',''),
                quantity_multiplier=strategy_data.get('quantity_multiplier',0),
                monday=strategy_data.get('monday',False),
                tuesday=strategy_data.get('tuesday',False),
                wednesday=strategy_data.get('wednesday',False),
                thrusday=strategy_data.get('thrusday',False),
                friday=strategy_data.get('friday',False),
                createdBy = strategy_data.get('createdBy',1),
                modifiedBy=strategy_data.get('modifiedBy',1)
                # Add other attributes as per your Strategy model
            )
            strategies.append(strategy)
            
            # Extract strategy variables
            strategy_variables_entry = strategy_data['strategyvariables']
                #(strategy_variables_entries)
            #print(5)
            variables = Variables(
                        id=strategy_variables_entry.get('id'),
                        portfolio_strategy_id=strategy.id,
                        underlying=strategy_variables_entry.get('underlying', ''),
                        strategy_type=strategy_variables_entry.get('strategy_type',''),
                        quantity_multiplier = strategy_variables_entry.get('quantity_multiplier', ''),
                        implied_futures_expiry=strategy_variables_entry.get('implied_futures_expiry',''),
                        entry_time=strategy_variables_entry.get('entry_time',''),
                        last_entry_time=strategy_variables_entry.get('last_entry_time',''),
                        exit_time=strategy_variables_entry.get('exit_time',''),
                        square_off=strategy_variables_entry.get('square_off',''),
                        overall_sl=strategy_variables_entry.get('overall_sl',0),
                        overall_target=strategy_variables_entry.get('overall_target',0),
                        trailing_options=strategy_variables_entry.get('trailing_options',''),
                        profit_reaches=strategy_variables_entry.get('profit_reaches',0),
                        lock_profit=strategy_variables_entry.get('lock_profit',0),
                        increase_in_profit=strategy_variables_entry.get('increase_in_profit',0),
                        trail_profit=strategy_variables_entry.get('trail_profit',0),
                        createdBy=strategy_variables_entry.get('createdBy',1),
                        modifiedBy=strategy_variables_entry.get('modifiedBy',1)
                        # Add other attributes as per your Variables model
                        
                    )
            #print(8)
            strategy_variables.append(variables)
                
                # Extract legs
            #print(strategy_variables_entry['legs'])
            strategy_legs = strategy_variables_entry['legs']
            for leg_entry in strategy_legs:
                leg = Leg(
                                id=leg_entry['id'],
                                portfolio_strategy_variables_id=variables.id,
                                lots=leg_entry['lots'],
                                position=leg_entry['position'],
                                option_type=leg_entry['option_type'],
                                expiry=leg_entry['expiry'],
                                no_of_reentry=leg_entry['no_of_reentry'],
                                strike_selection_criteria=leg_entry.get('strike_selection_criteria'),
                                closest_premium=leg_entry.get('closest_premium'),
                                strike_type=leg_entry.get('strike_type'),
                                straddle_width_value=leg_entry.get('straddle_width_value'),
                                straddle_width_sign=leg_entry.get('straddle_width_sign'),
                                percent_of_atm_strike_value=leg_entry.get('percent_of_atm_strike_value'),
                                percent_of_atm_strike_sign=leg_entry.get('percent_of_atm_strike_sign'),
                                atm_straddle_premium=leg_entry.get('atm_straddle_premium'),
                                strike_selection_criteria_stop_loss=leg_entry.get('strike_selection_criteria_stop_loss'),
                                strike_selection_criteria_stop_loss_sign=leg_entry.get('strike_selection_criteria_stop_loss_sign'),
                                strike_selection_criteria_trailing_options=leg_entry.get('strike_selection_criteria_trailing_options'),
                                strike_selection_criteria_profit_reaches=leg_entry.get('strike_selection_criteria_profit_reaches'),
                                strike_selection_criteria_lock_profit=leg_entry.get('strike_selection_criteria_lock_profit'),
                                strike_selection_criteria_lock_profit_sign=leg_entry.get('strike_selection_criteria_lock_profit_sign'),
                                strike_selection_criteria_increase_in_profit=leg_entry.get('strike_selection_criteria_increase_in_profit'),
                                strike_selection_criteria_trail_profit=leg_entry.get('strike_selection_criteria_trail_profit'),
                                strike_selection_criteria_trail_profit_sign=leg_entry.get('strike_selection_criteria_trail_profit_sign'),
                                roll_strike=leg_entry.get('roll_strike'),
                                roll_strike_strike_type=leg_entry.get('roll_strike_strike_type'),
                                roll_strike_stop_loss=leg_entry.get('roll_strike_stop_loss'),
                                roll_strike_stop_loss_sign=leg_entry.get('roll_strike_stop_loss_sign'),
                                roll_strike_trailing_options=leg_entry.get('roll_strike_trailing_options'),
                                roll_strike_profit_reaches=leg_entry.get('roll_strike_profit_reaches'),
                                roll_strike_lock_profit=leg_entry.get('roll_strike_lock_profit'),
                                roll_strike_lock_profit_sign=leg_entry.get('roll_strike_lock_profit_sign'),
                                roll_strike_increase_in_profit=leg_entry.get('roll_strike_increase_in_profit'),
                                roll_strike_trail_profit=leg_entry.get('roll_strike_trail_profit'),
                                roll_strike_trail_profit_sign=leg_entry.get('roll_strike_trail_profit_sign'),
                                simple_momentum_range_breakout=leg_entry.get('simple_momentum_range_breakout'),
                                simple_momentum=leg_entry.get('simple_momentum'),
                                simple_momentum_sign=leg_entry.get('simple_momentum_sign'),
                                simple_momentum_direction=leg_entry.get('simple_momentum_direction'),
                                range_breakout=leg_entry.get('range_breakout'),
                                createdBy = leg_entry.get('createdBy',1),
                                modifiedBy=leg_entry.get('modifiedBy',1)
                                # Add other attributes as per your Leg model
                            )
                legs.append(leg)
            
    
            # Assuming PortfolioRepo is responsible for data insertion
            repo = PortfolioRepo()
            repo.insert_data(portfolio, strategies, strategy_variables, legs)
            strategies = []
            strategy_variables = []
            legs = []
      
    def process_update_data(self, data,strategyId):
    
        strategies = []
        strategy_variables = []
        legs = []
    
    
        # Create Portfolio object
        portfolio = Portfolio(id=self.data.get('id'), name=self.data.get('name'),createdBy=self.data.get('createdBy',0),modifiedBy=self.data.get('modifiedBy',0))
        
        
        repo = PortfolioRepo()
        repo.update_portfolio(portfolio,strategyId)
        
        #Deleting record which do not needed
        refactor_strategy(data['strategies'],strategyId)
        
        #Insert and update
        for strategy_data in data['strategies']: 
            repo = PortfolioRepo()
            strategy_id = repo.portfolio_strategy_insert_update(strategy_data,strategyId)
            
            variables = strategy_data['strategyvariables']
            portfolio_strategy_variable_id = repo.portfolio_strategy_variable_insert_update(variables,strategy_id)
            
            legs_data = variables['legs']   
            repo.portfolio_strategy_variable_leg_insert_update(legs_data,portfolio_strategy_variable_id)
            
    def var_update(self, data,statVarId):
        
        repo = PortfolioRepo()
       # print(1)
        repo.update_variables(data,statVarId)
        #print(3)
        legs_data = data['legs']  
        refactor_legs(legs_data,statVarId)
        repo.portfolio_strategy_variable_leg_insert_update(legs_data,statVarId)
        #newdata = repo.getstrategyvariables(statVarId)
        #return 
        
    def getAllPortfolioDetails(self):
        repo = PortfolioRepo()
        strategy_name = repo.getAllPortfolio()
        return strategy_name
    
    def getPortfolioDetails(self, strategyId):
        print(strategyId)
        repo = PortfolioRepo()
        strategy_details = repo.getPortfolioDetails(strategyId)
        return strategy_details
    
class Portfolio:
    def __init__(self, id: int, name: str, createdBy: int, modifiedBy: int):
        self.id = id
        self.name = name  # Remove the trailing comma to prevent it from being a tuple
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy

    def __repr__(self):  # Correct the method name to '__repr__'
        return f"Portfolio(id={self.id}, name={self.name}, createdBy={self.createdBy}, modifiedBy={self.modifiedBy})"

class Strategy:
    def __init__(self,id:int,portfolio_id:int,strategy_id:int,symbol:str,quantity_multiplier:int,monday:bool,tuesday:bool,wednesday:bool,thrusday:bool,friday:bool,createdBy:int,modifiedBy:int):
            #print(id)
            #print(position)
        self.id = id
        self.portfolio_id = portfolio_id
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.quantity_multiplier = quantity_multiplier
        self.monday = bool(monday)  # Convert to boolean
        self.tuesday = bool(tuesday)  # Convert to boolean
        self.wednesday = bool(wednesday)
        self.thrusday = bool(thrusday)
        self.friday = bool(friday)
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        #print(1)
        
    def _repr_(self):
        #print(self.id)
        return f"Strategy(id={self.id},portfolio_id={self.portfolio_id},strategy_id={self.strategy_id},symbol={self.symbol},quantity_multiplier={self.quantity_multiplier},monday={self.monday},tuesday={self.tuesday},wednesday={self.wednesday},thrusday={self.thrusday},friday={self.friday},createdBy={self.createdBy},modifiedBy={self.modifiedBy})"
    
    
class Variables:
    def __init__(self,id:int,portfolio_strategy_id:int,underlying:str,strategy_type:str,quantity_multiplier:str,implied_futures_expiry:str,entry_time:str,last_entry_time:str,exit_time:str,square_off:str,overall_sl:int,overall_target:int,trailing_options:str,profit_reaches:int,lock_profit:int,increase_in_profit:int,trail_profit:int,createdBy:int,modifiedBy:int):
        #print(id)
        self.id = id
        self.portfolio_strategy_id=portfolio_strategy_id
        self.underlying=underlying
        self.strategy_type=strategy_type
        self.quantity_multiplier = quantity_multiplier
        self.implied_futures_expiry=implied_futures_expiry
        self.entry_time=entry_time
        self.last_entry_time=last_entry_time
        self.exit_time=exit_time
        self.square_off=square_off
        self.overall_sl=overall_sl
        self.overall_target=overall_target
        self.trailing_options=trailing_options
        self.profit_reaches=profit_reaches
        self.lock_profit=lock_profit
        self.increase_in_profit=increase_in_profit
        self.trail_profit=trail_profit
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        #print(2)
        #print(self.id)

    def _repr_(self):
        #print(self.id)
        return f"Variables(id={self.id},name={self.name},underlying={self.underlying},strategy_type={self.strategy_type},quantity_multiplier={self.quantity_multiplier},implied_futures_expiry={self.implied_futures_expiry},entry_time={self.entry_time},last_entry_time={self.last_entry_time},exit_time={self.exit_time},square_off={self.square_off},overall_sl={self.overall_sl},overall_target={self.overall_target},trailing_options={self.trailing_options},profit_reaches={self.profit_reaches},lock_profit={self.lock_profit},increase_in_profit={self.increase_in_profit},trail_profit={self.trail_profit},createdBy={self.createdBy},modifiedBy={self.modifiedBy})"

class Leg:
    def __init__(self,id:int,portfolio_strategy_variables_id:int ,lots:int,position:str,option_type:str,expiry:str,no_of_reentry:int,strike_selection_criteria:str,closest_premium:int,strike_type:str,straddle_width_value:str,straddle_width_sign:str,percent_of_atm_strike_value:str,percent_of_atm_strike_sign:str,atm_straddle_premium:int,strike_selection_criteria_stop_loss:int,strike_selection_criteria_stop_loss_sign:str,strike_selection_criteria_trailing_options:str,strike_selection_criteria_profit_reaches:int,strike_selection_criteria_lock_profit:int,strike_selection_criteria_lock_profit_sign:str,strike_selection_criteria_increase_in_profit:int,strike_selection_criteria_trail_profit:int,strike_selection_criteria_trail_profit_sign:str,roll_strike:int,roll_strike_strike_type:str,roll_strike_stop_loss:int,roll_strike_stop_loss_sign:str,roll_strike_trailing_options:str,roll_strike_profit_reaches:int,roll_strike_lock_profit:int,roll_strike_lock_profit_sign:str,roll_strike_increase_in_profit:int,roll_strike_trail_profit:int,roll_strike_trail_profit_sign:str,simple_momentum_range_breakout:str,simple_momentum:int,simple_momentum_sign:str,simple_momentum_direction:str,range_breakout:str,createdBy:int,modifiedBy:int):
            #print(id)
            #print(position)
        self.id = id
        self.portfolio_strategy_variables_id = portfolio_strategy_variables_id
        self.lots = lots
        self.position = position
        self.option_type = option_type
        self.expiry = expiry
        self.no_of_reentry = no_of_reentry
        self.strike_selection_criteria = strike_selection_criteria
        self.closest_premium = closest_premium
        self.strike_type = strike_type
        self.straddle_width_value = straddle_width_value
        self.straddle_width_sign = straddle_width_sign
        self.percent_of_atm_strike_value = percent_of_atm_strike_value
        self.percent_of_atm_strike_sign = percent_of_atm_strike_sign
        self.atm_straddle_premium = atm_straddle_premium
        self.strike_selection_criteria_stop_loss = strike_selection_criteria_stop_loss
        self.strike_selection_criteria_stop_loss_sign = strike_selection_criteria_stop_loss_sign
        self.strike_selection_criteria_trailing_options = strike_selection_criteria_trailing_options
        self.strike_selection_criteria_profit_reaches = strike_selection_criteria_profit_reaches
        self.strike_selection_criteria_lock_profit = strike_selection_criteria_lock_profit
        self.strike_selection_criteria_lock_profit_sign = strike_selection_criteria_lock_profit_sign
        self.strike_selection_criteria_increase_in_profit = strike_selection_criteria_increase_in_profit
        self.strike_selection_criteria_trail_profit = strike_selection_criteria_trail_profit
        self.strike_selection_criteria_trail_profit_sign = strike_selection_criteria_trail_profit_sign
        self.roll_strike = roll_strike
        self.roll_strike_strike_type = roll_strike_strike_type
        self.roll_strike_stop_loss = roll_strike_stop_loss
        self.roll_strike_stop_loss_sign = roll_strike_stop_loss_sign
        self.roll_strike_trailing_options = roll_strike_trailing_options
        self.roll_strike_profit_reaches = roll_strike_profit_reaches
        self.roll_strike_lock_profit = roll_strike_lock_profit
        self.roll_strike_lock_profit_sign = roll_strike_lock_profit_sign
        self.roll_strike_increase_in_profit = roll_strike_increase_in_profit
        self.roll_strike_trail_profit = roll_strike_trail_profit
        self.roll_strike_trail_profit_sign = roll_strike_trail_profit_sign
        self.simple_momentum_range_breakout = simple_momentum_range_breakout
        self.simple_momentum = simple_momentum
        self.simple_momentum_sign = simple_momentum_sign
        self.simple_momentum_direction = simple_momentum_direction
        self.range_breakout = range_breakout
        self.createdBy = createdBy,
        self.modifiedBy = modifiedBy
        #print(self.position)
        #print(4)
    def _repr_(self):
        #print(self.id)
        return f"Leg(id={self.id},strategy_id={self.strategy_id},leg_no={self.leg_no},lots={self.lots},position={self.position},option_type={self.option_type},expiry={self.expiry},no_of_reentry={self.no_of_reentry},strike_selection_criteria={self.strike_selection_criteria},closest_premium={self.closest_premium},strike_type={self.strike_type},straddle_width_value={self.straddle_width_value},straddle_width_sign={self.straddle_width_sign},percent_of_atm_strike_value={self.percent_of_atm_strike_value},percent_of_atm_strike_sign={self.percent_of_atm_strike_sign},atm_straddle_premium={self.atm_straddle_premium},strike_selection_criteria_stop_loss={self.strike_selection_criteria_stop_loss},strike_selection_criteria_stop_loss_sign={self.strike_selection_criteria_stop_loss_sign},strike_selection_criteria_trailing_options={self.strike_selection_criteria_trailing_options},strike_selection_criteria_profit_reaches={self.strike_selection_criteria_profit_reaches},strike_selection_criteria_lock_profit={self.strike_selection_criteria_lock_profit},strike_selection_criteria_lock_profit_sign={self.strike_selection_criteria_lock_profit_sign},strike_selection_criteria_increase_in_profit={self.strike_selection_criteria_increase_in_profit},strike_selection_criteria_trail_profit={self.strike_selection_criteria_trail_profit},strike_selection_criteria_trail_profit_sign={self.strike_selection_criteria_trail_profit_sign},roll_strike={self.roll_strike},roll_strike_strike_type={self.roll_strike_strike_type},roll_strike_stop_loss={self.roll_strike_stop_loss},roll_strike_stop_loss_sign={self.roll_strike_stop_loss_sign},roll_strike_trailing_options={self.roll_strike_trailing_options},roll_strike_profit_reaches={self.roll_strike_profit_reaches},roll_strike_lock_profit={self.roll_strike_lock_profit},roll_strike_lock_profit_sign={self.roll_strike_lock_profit_sign},roll_strike_increase_in_profit={self.roll_strike_increase_in_profit},roll_strike_trail_profit={self.roll_strike_trail_profit},roll_strike_trail_profit_sign={self.roll_strike_trail_profit_sign},simple_momentum_range_breakout={self.simple_momentum_range_breakout},simple_momentum={self.simple_momentum},simple_momentum_sign={self.simple_momentum_sign},simple_momentum_direction={self.simple_momentum_direction},range_breakout={self.range_breakout},createdBy={self.createdBy},modifiedBy={self.modifiedBy})"