
from repo.straddlerepo import StraddleRepo
import json

        
class Strategyservice:
    def __init__(self,data):
        self.data = data

        #self.strategyId = strategyId
    
    def process_insert_data(self, data):
        #strategy = Strategy(id = data['strategies'][0]['id'], name= data['strategies'][0]['name'],underlying= data['strategies'][0]['underlying'],strategy_type= data['strategies'][0]['strategy_type'],implied_futures_expiry= data['strategies'][0]['implied_futures_expiry'],entry_time= data['strategies'][0]['entry_time'],last_entry_time= data['strategies'][0]['last_entry_time'],exit_time= data['strategies'][0]['exit_time'],square_off= data['strategies'][0]['square_off'],overall_sl= data['strategies'][0]['overall_sl'],overall_target= data['strategies'][0]['overall_target'],trailing_options= data['strategies'][0]['trailing_options'],profit_reaches= data['strategies'][0]['profit_reaches'],lock_profit= data['strategies'][0]['lock_profit'],increase_in_profit= data['strategies'][0]['increase_in_profit'],trail_profit= data['strategies'][0]['trail_profit'])
        createdBy = self.data['strategies'].get('createdBy')
        print(f"created by = {createdBy}")
        strategy = Strategy(
            id=self.data['strategies'].get('id'),
            name=self.data['strategies'].get('name'),
            underlying=self.data['strategies'].get('underlying', ''),
            strategy_type=self.data['strategies'].get('strategy_type', ''),
            implied_futures_expiry=self.data['strategies'].get('implied_futures_expiry', ''),
            entry_time=self.data['strategies'].get('entry_time', ''),
            last_entry_time=self.data['strategies'].get('last_entry_time', ''),
            exit_time=self.data['strategies'].get('exit_time', ''),
            square_off=self.data['strategies'].get('square_off', ''),
            overall_sl=self.data['strategies'].get('overall_sl', 0),
            overall_target=self.data['strategies'].get('overall_target', 0),
            trailing_options=self.data['strategies'].get('trailing_options', ''),
            profit_reaches=self.data['strategies'].get('profit_reaches', 0),
            lock_profit=self.data['strategies'].get('lock_profit', 0),
            increase_in_profit=self.data['strategies'].get('increase_in_profit', 0),
            trail_profit=self.data['strategies'].get('trail_profit', 0),
            createdBy=self.data['strategies'].get('createdBy', 1),
            modifiedBy=self.data['strategies'].get('modifiedBy',1)

        )

        legs = []
        #print(data['strategies'][0]['legs'])

        for leg_data in self.data['strategies']['legs']:
            leg = Leg(
                id=leg_data.get('id'),
                    strategy_id=strategy.id,
                    leg_no=leg_data.get('leg_no', 0),
                    lots=leg_data.get('lots', 0),
                    position=leg_data.get('position', ''),
                    option_type=leg_data.get('option_type', ''),
                    expiry=leg_data.get('expiry', ''),
                    no_of_reentry=leg_data.get('no_of_reentry', 0),
                    strike_selection_criteria=leg_data.get('strike_selection_criteria', ''),
                    closest_premium=leg_data.get('closest_premium', 0),
                    strike_type=leg_data.get('strike_type', ''),
                    straddle_width_value=leg_data.get('straddle_width_value', ''),
                    straddle_width_sign=leg_data.get('straddle_width_sign', ''),
                    percent_of_atm_strike_value=leg_data.get('percent_of_atm_strike_value', ''),
                    percent_of_atm_strike_sign=leg_data.get('percent_of_atm_strike_sign', ''),
                    atm_straddle_premium=leg_data.get('atm_straddle_premium', 0),
                    strike_selection_criteria_stop_loss=leg_data.get('strike_selection_criteria_stop_loss', 0),
                    strike_selection_criteria_stop_loss_sign=leg_data.get('strike_selection_criteria_stop_loss_sign', ''),
                    strike_selection_criteria_trailing_options=leg_data.get('strike_selection_criteria_trailing_options', ''),
                    strike_selection_criteria_profit_reaches=leg_data.get('strike_selection_criteria_profit_reaches', 0),
                    strike_selection_criteria_lock_profit=leg_data.get('strike_selection_criteria_lock_profit', 0),
                    strike_selection_criteria_lock_profit_sign=leg_data.get('strike_selection_criteria_lock_profit_sign', ''),
                    strike_selection_criteria_increase_in_profit=leg_data.get('strike_selection_criteria_increase_in_profit', 0),
                    strike_selection_criteria_trail_profit=leg_data.get('strike_selection_criteria_trail_profit', 0),
                    strike_selection_criteria_trail_profit_sign=leg_data.get('strike_selection_criteria_trail_profit_sign', ''),
                    roll_strike=leg_data.get('roll_strike', 0),
                    roll_strike_strike_type=leg_data.get('roll_strike_strike_type', ''),
                    roll_strike_stop_loss=leg_data.get('roll_strike_stop_loss', 0),
                    roll_strike_stop_loss_sign=leg_data.get('roll_strike_stop_loss_sign', ''),
                    roll_strike_trailing_options=leg_data.get('roll_strike_trailing_options', ''),
                    roll_strike_profit_reaches=leg_data.get('roll_strike_profit_reaches', 0),
                    roll_strike_lock_profit=leg_data.get('roll_strike_lock_profit', 0),
                    roll_strike_lock_profit_sign=leg_data.get('roll_strike_lock_profit_sign', ''),
                    roll_strike_increase_in_profit=leg_data.get('roll_strike_increase_in_profit', 0),
                    roll_strike_trail_profit=leg_data.get('roll_strike_trail_profit', 0),
                    roll_strike_trail_profit_sign=leg_data.get('roll_strike_trail_profit_sign', ''),
                    simple_momentum_range_breakout=leg_data.get('simple_momentum_range_breakout', ''),
                    simple_momentum=leg_data.get('simple_momentum', 0),
                    simple_momentum_sign=leg_data.get('simple_momentum_sign', ''),
                    simple_momentum_direction=leg_data.get('simple_momentum_direction', ''),
                    range_breakout=leg_data.get('range_breakout', ''),
                    createdBy=leg_data.get('createdBy', 1),
                    modifiedBy = leg_data.get('modifiedBy', 1)
                )
            #print(leg.position)
            legs.append(leg)
        #print(len(legs))
            
        # Do data validation
   
        # Pass data to repo
        repo = StraddleRepo()
        repo.insert_data(strategy,legs)
     
    
    def process_update_data(self, data,strategyId):
        strategy = Strategy(
            id=self.data['strategies'].get('id'),
            name=self.data['strategies'].get('name'),
            underlying=self.data['strategies'].get('underlying', ''),
            strategy_type=self.data['strategies'].get('strategy_type', ''),
            implied_futures_expiry=self.data['strategies'].get('implied_futures_expiry', ''),
            entry_time=self.data['strategies'].get('entry_time', ''),
            last_entry_time=self.data['strategies'].get('last_entry_time', ''),
            exit_time=self.data['strategies'].get('exit_time', ''),
            square_off=self.data['strategies'].get('square_off', ''),
            overall_sl=self.data['strategies'].get('overall_sl', 0),
            overall_target=self.data['strategies'].get('overall_target', 0),
            trailing_options=self.data['strategies'].get('trailing_options', ''),
            profit_reaches=self.data['strategies'].get('profit_reaches', 0),
            lock_profit=self.data['strategies'].get('lock_profit', 0),
            increase_in_profit=self.data['strategies'].get('increase_in_profit', 0),
            trail_profit=self.data['strategies'].get('trail_profit', 0),
            createdBy = self.data['strategies'].get('createdBy',1),
            modifiedBy = self.data['strategies'].get('modifiedBy', 1)
        )
        
        legs = []
        #print(data['strategies'][0]['legs'])

        for leg_data in self.data['strategies']['legs']:
            leg = Leg(
                id=leg_data.get('id'),
                    strategy_id=strategy.id,
                    leg_no=leg_data.get('leg_no', 0),
                    lots=leg_data.get('lots', 0),
                    position=leg_data.get('position', ''),
                    option_type=leg_data.get('option_type', ''),
                    expiry=leg_data.get('expiry', ''),
                    no_of_reentry=leg_data.get('no_of_reentry', 0),
                    strike_selection_criteria=leg_data.get('strike_selection_criteria', ''),
                    closest_premium=leg_data.get('closest_premium', 0),
                    strike_type=leg_data.get('strike_type', ''),
                    straddle_width_value=leg_data.get('straddle_width_value', ''),
                    straddle_width_sign=leg_data.get('straddle_width_sign', ''),
                    percent_of_atm_strike_value=leg_data.get('percent_of_atm_strike_value', ''),
                    percent_of_atm_strike_sign=leg_data.get('percent_of_atm_strike_sign', ''),
                    atm_straddle_premium=leg_data.get('atm_straddle_premium', 0),
                    strike_selection_criteria_stop_loss=leg_data.get('strike_selection_criteria_stop_loss', 0),
                    strike_selection_criteria_stop_loss_sign=leg_data.get('strike_selection_criteria_stop_loss_sign', ''),
                    strike_selection_criteria_trailing_options=leg_data.get('strike_selection_criteria_trailing_options', ''),
                    strike_selection_criteria_profit_reaches=leg_data.get('strike_selection_criteria_profit_reaches', 0),
                    strike_selection_criteria_lock_profit=leg_data.get('strike_selection_criteria_lock_profit', 0),
                    strike_selection_criteria_lock_profit_sign=leg_data.get('strike_selection_criteria_lock_profit_sign', ''),
                    strike_selection_criteria_increase_in_profit=leg_data.get('strike_selection_criteria_increase_in_profit', 0),
                    strike_selection_criteria_trail_profit=leg_data.get('strike_selection_criteria_trail_profit', 0),
                    strike_selection_criteria_trail_profit_sign=leg_data.get('strike_selection_criteria_trail_profit_sign', ''),
                    roll_strike=leg_data.get('roll_strike', 0),
                    roll_strike_strike_type=leg_data.get('roll_strike_strike_type', ''),
                    roll_strike_stop_loss=leg_data.get('roll_strike_stop_loss', 0),
                    roll_strike_stop_loss_sign=leg_data.get('roll_strike_stop_loss_sign', ''),
                    roll_strike_trailing_options=leg_data.get('roll_strike_trailing_options', ''),
                    roll_strike_profit_reaches=leg_data.get('roll_strike_profit_reaches', 0),
                    roll_strike_lock_profit=leg_data.get('roll_strike_lock_profit', 0),
                    roll_strike_lock_profit_sign=leg_data.get('roll_strike_lock_profit_sign', ''),
                    roll_strike_increase_in_profit=leg_data.get('roll_strike_increase_in_profit', 0),
                    roll_strike_trail_profit=leg_data.get('roll_strike_trail_profit', 0),
                    roll_strike_trail_profit_sign=leg_data.get('roll_strike_trail_profit_sign', ''),
                    simple_momentum_range_breakout=leg_data.get('simple_momentum_range_breakout', ''),
                    simple_momentum=leg_data.get('simple_momentum', 0),
                    simple_momentum_sign=leg_data.get('simple_momentum_sign', ''),
                    simple_momentum_direction=leg_data.get('simple_momentum_direction', ''),
                    range_breakout=leg_data.get('range_breakout', ''),
                    createdBy = self.data['strategies'].get('createdBy', 1),
                    modifiedBy = self.data['strategies'].get('modifiedBy', 1)
                )
            #print(leg.position)
            legs.append(leg)
        #print(len(legs))
            
        # Do data validation
        
        # Pass data to repo
        repo = StraddleRepo()
        repo.update_data(strategy,legs,strategyId)
        
    def getStrategyName(self):
        repo = StraddleRepo()
        strategy_name = repo.getStrategyName()
        return strategy_name
        
    def getStrategyDetails(self, strategyId):
        print(strategyId)
        repo = StraddleRepo()
        strategy_details = repo.getStrategyDetails(strategyId)
        return strategy_details
     
    def getAllStrategyDetails(self):
        repo = StraddleRepo()
        strategy_name = repo.getAllStrategies()
        return strategy_name
        
    
class Strategy:
    def __init__(self,id:int,name:str,underlying:str,strategy_type:str,implied_futures_expiry:str,entry_time:str,last_entry_time:str,exit_time:str,square_off:str,overall_sl:int,overall_target:int,trailing_options:str,profit_reaches:int,lock_profit:int,increase_in_profit:int,trail_profit:int,createdBy:int,modifiedBy:int):
        #print(id)
        self.id = id
        self.name=name
        self.underlying=underlying
        self.strategy_type=strategy_type
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
        
        #print(self.id)

    def _repr_(self):
        #print(self.id)
        return f"Strategy(id={self.id},name={self.name},underlying={self.underlying},strategy_type={self.strategy_type},implied_futures_expiry={self.implied_futures_expiry},entry_time={self.entry_time},last_entry_time={self.last_entry_time},exit_time={self.exit_time},square_off={self.square_off},overall_sl={self.overall_sl},overall_target={self.overall_target},trailing_options={self.trailing_options},profit_reaches={self.profit_reaches},lock_profit={self.lock_profit},increase_in_profit={self.increase_in_profit},trail_profit={self.trail_profit},createdBy={self.createdBy},modifiedBy={self.modifiedBy})"
    

class Leg:
    def __init__(self,id:int,strategy_id:int,leg_no:int,lots:int,position:str,option_type:str,expiry:str,no_of_reentry:int,strike_selection_criteria:str,closest_premium:int,strike_type:str,straddle_width_value:str,straddle_width_sign:str,percent_of_atm_strike_value:str,percent_of_atm_strike_sign:str,atm_straddle_premium:int,strike_selection_criteria_stop_loss:int,strike_selection_criteria_stop_loss_sign:str,strike_selection_criteria_trailing_options:str,strike_selection_criteria_profit_reaches:int,strike_selection_criteria_lock_profit:int,strike_selection_criteria_lock_profit_sign:str,strike_selection_criteria_increase_in_profit:int,strike_selection_criteria_trail_profit:int,strike_selection_criteria_trail_profit_sign:str,roll_strike:int,roll_strike_strike_type:str,roll_strike_stop_loss:int,roll_strike_stop_loss_sign:str,roll_strike_trailing_options:str,roll_strike_profit_reaches:int,roll_strike_lock_profit:int,roll_strike_lock_profit_sign:str,roll_strike_increase_in_profit:int,roll_strike_trail_profit:int,roll_strike_trail_profit_sign:str,simple_momentum_range_breakout:str,simple_momentum:int,simple_momentum_sign:str,simple_momentum_direction:str,range_breakout:str,createdBy:int,modifiedBy:int):
            #print(id)
            #print(position)
        self.id = id
        self.strategy_id = strategy_id
        self.leg_no = leg_no
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
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        #print(self.position)
            
    def _repr_(self):
        #print(self.id)
        return f"Leg(id={self.id},strategy_id={self.strategy_id},leg_no={self.leg_no},lots={self.lots},position={self.position},option_type={self.option_type},expiry={self.expiry},no_of_reentry={self.no_of_reentry},strike_selection_criteria={self.strike_selection_criteria},closest_premium={self.closest_premium},strike_type={self.strike_type},straddle_width_value={self.straddle_width_value},straddle_width_sign={self.straddle_width_sign},percent_of_atm_strike_value={self.percent_of_atm_strike_value},percent_of_atm_strike_sign={self.percent_of_atm_strike_sign},atm_straddle_premium={self.atm_straddle_premium},strike_selection_criteria_stop_loss={self.strike_selection_criteria_stop_loss},strike_selection_criteria_stop_loss_sign={self.strike_selection_criteria_stop_loss_sign},strike_selection_criteria_trailing_options={self.strike_selection_criteria_trailing_options},strike_selection_criteria_profit_reaches={self.strike_selection_criteria_profit_reaches},strike_selection_criteria_lock_profit={self.strike_selection_criteria_lock_profit},strike_selection_criteria_lock_profit_sign={self.strike_selection_criteria_lock_profit_sign},strike_selection_criteria_increase_in_profit={self.strike_selection_criteria_increase_in_profit},strike_selection_criteria_trail_profit={self.strike_selection_criteria_trail_profit},strike_selection_criteria_trail_profit_sign={self.strike_selection_criteria_trail_profit_sign},roll_strike={self.roll_strike},roll_strike_strike_type={self.roll_strike_strike_type},roll_strike_stop_loss={self.roll_strike_stop_loss},roll_strike_stop_loss_sign={self.roll_strike_stop_loss_sign},roll_strike_trailing_options={self.roll_strike_trailing_options},roll_strike_profit_reaches={self.roll_strike_profit_reaches},roll_strike_lock_profit={self.roll_strike_lock_profit},roll_strike_lock_profit_sign={self.roll_strike_lock_profit_sign},roll_strike_increase_in_profit={self.roll_strike_increase_in_profit},roll_strike_trail_profit={self.roll_strike_trail_profit},roll_strike_trail_profit_sign={self.roll_strike_trail_profit_sign},simple_momentum_range_breakout={self.simple_momentum_range_breakout},simple_momentum={self.simple_momentum},simple_momentum_sign={self.simple_momentum_sign},simple_momentum_direction={self.simple_momentum_direction},range_breakout={self.range_breakout},createdBy={self.createdBy},modifiedBy={self.modifiedBy})"