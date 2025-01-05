from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
from Strategy import Strategy  
from LegBuilder import LegBuilder 
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
url = "http://localhost:8000/run_strategies/"
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class Leg(BaseModel):
    atm_straddle_premium: Any
    closest_premium: Any
    expiry: Any
    id: Any
    leg_no: Any
    lots: Any
    no_of_reentry: Any
    option_type: Any
    percent_of_atm_strike_sign: Any
    percent_of_atm_strike_value: Any
    position: Any
    range_breakout: Any
    roll_strike: Any
    roll_strike_increase_in_profit: Any
    roll_strike_lock_profit: Any
    roll_strike_lock_profit_sign: Any
    roll_strike_profit_reaches: Any
    roll_strike_stop_loss: Any
    roll_strike_stop_loss_sign: Any
    roll_strike_strike_type: Any
    roll_strike_trail_profit: Any
    roll_strike_trail_profit_sign: Any
    roll_strike_trailing_options: Any
    simple_momentum: Any
    simple_momentum_direction: Any
    simple_momentum_range_breakout: Any
    simple_momentum_sign: Any
    straddle_width_sign: Any
    straddle_width_value: Any
    strategy_id: Any
    strike_selection_criteria: Any
    strike_selection_criteria_increase_in_profit: Any
    strike_selection_criteria_lock_profit: Any
    strike_selection_criteria_lock_profit_sign: Any
    strike_selection_criteria_profit_reaches: Any
    strike_selection_criteria_stop_loss: Any
    strike_selection_criteria_stop_loss_sign: Any
    strike_selection_criteria_trail_profit: Any
    strike_selection_criteria_trail_profit_sign: Any
    strike_selection_criteria_trailing_options: Any
    strike_type: Any

class OverallStrategy(BaseModel):
    id: Any
    name: Any
    underlying: Any
    strategy_type: Any
    implied_futures_expiry: Any
    entry_time: Any
    last_entry_time: Any
    exit_time: Any
    square_off: Any
    overall_sl: Any
    overall_target: Any
    trailing_options: Any
    profit_reaches: Any
    lock_profit: Any
    increase_in_profit: Any
    trail_profit: Any
    legs: List[Leg] 
    fromdate: Any
    todate: Any
    index: Any

def map_leg_to_legbuilder(leg_data: Leg) -> LegBuilder:
    return LegBuilder(
        atm_straddle_premium=leg_data.atm_straddle_premium,
        closest_premium=leg_data.closest_premium,
        expiry=leg_data.expiry,
        id=leg_data.id,
        leg_no=leg_data.leg_no,
        lots=leg_data.lots,
        no_of_reentry=leg_data.no_of_reentry,
        option_type="CE" if leg_data.option_type=="call" else "PE",
        percent_of_atm_strike_sign=leg_data.percent_of_atm_strike_sign,
        percent_of_atm_strike_value=leg_data.percent_of_atm_strike_value,
        position=leg_data.position,
        range_breakout=leg_data.range_breakout,
        roll_strike=leg_data.roll_strike,
        roll_strike_increase_in_profit=leg_data.roll_strike_increase_in_profit,
        roll_strike_lock_profit=leg_data.roll_strike_lock_profit,
        roll_strike_lock_profit_sign=leg_data.roll_strike_lock_profit_sign,
        roll_strike_profit_reaches=leg_data.roll_strike_profit_reaches,
        roll_strike_stop_loss=leg_data.roll_strike_stop_loss,
        roll_strike_stop_loss_sign=leg_data.roll_strike_stop_loss_sign,
        roll_strike_strike_type=leg_data.roll_strike_strike_type,
        roll_strike_trail_profit=leg_data.roll_strike_trail_profit,
        roll_strike_trail_profit_sign=leg_data.roll_strike_trail_profit_sign,
        roll_strike_trailing_options=leg_data.roll_strike_trailing_options,
        simple_momentum=leg_data.simple_momentum,
        simple_momentum_direction=leg_data.simple_momentum_direction,
        simple_momentum_range_breakout=leg_data.simple_momentum_range_breakout,
        simple_momentum_sign=leg_data.simple_momentum_sign,
        straddle_width_sign=leg_data.straddle_width_sign,
        straddle_width_value=leg_data.straddle_width_value,
        strategy_id=leg_data.strategy_id,
        strike_selection_criteria=leg_data.strike_selection_criteria,
        strike_selection_criteria_increase_in_profit=leg_data.strike_selection_criteria_increase_in_profit,
        strike_selection_criteria_lock_profit=leg_data.strike_selection_criteria_lock_profit,
        strike_selection_criteria_lock_profit_sign=leg_data.strike_selection_criteria_lock_profit_sign,
        strike_selection_criteria_profit_reaches=leg_data.strike_selection_criteria_profit_reaches,
        strike_selection_criteria_stop_loss=leg_data.strike_selection_criteria_stop_loss,
        strike_selection_criteria_stop_loss_sign=leg_data.strike_selection_criteria_stop_loss_sign,
        strike_selection_criteria_trail_profit=leg_data.strike_selection_criteria_trail_profit,
        strike_selection_criteria_trail_profit_sign=leg_data.strike_selection_criteria_trail_profit_sign,
        strike_selection_criteria_trailing_options=leg_data.strike_selection_criteria_trailing_options,
        strike_type=leg_data.strike_type
    )

def map_strategy_to_strategy_class(overall_strategy: OverallStrategy) -> Strategy:
    return Strategy(
        id=overall_strategy.id,
        name=overall_strategy.name,
        underlying='spot' if overall_strategy.underlying=='spot' else 'implied_futures' if overall_strategy.underlying =='implied futures' else 'fut',
        strategy_type=overall_strategy.strategy_type,
        implied_futures_expiry=overall_strategy.implied_futures_expiry,
        entry_time=overall_strategy.entry_time,
        last_entry_time=overall_strategy.last_entry_time,
        exit_time=overall_strategy.exit_time,
        square_off=overall_strategy.square_off,
        overall_sl=overall_strategy.overall_sl,
        overall_target=overall_strategy.overall_target,
        trailing_options=overall_strategy.trailing_options,
        profit_reaches=overall_strategy.profit_reaches,
        lock_profit=overall_strategy.lock_profit,
        increase_in_profit=overall_strategy.increase_in_profit,
        trail_profit=overall_strategy.trail_profit,
        legs=[map_leg_to_legbuilder(leg) for leg in overall_strategy.legs],
        fromdate=overall_strategy.fromdate,
        todate=overall_strategy.todate,
        index=overall_strategy.index
    )

@app.post("/run_strategies/")
async def receive_strategy(overall_strategy: OverallStrategy):
    try:
        # print(overall_strategy)
        payload = [{
            "strategy_details": {
                "name": overall_strategy.name,
                "index": "NIFTY 50" if overall_strategy.index.lower() =='nifty' else "NIFTY BANK" if overall_strategy.index.lower() =='banknifty' else "NIFTY FIN SERVICE",
                "underlying": 'spot' if overall_strategy.underlying=='spot' else 'implied_futures' if overall_strategy.underlying =='impliedfutures' else 'futures',
                "strategy_type": overall_strategy.strategy_type,
                "start_date": overall_strategy.fromdate,
                "end_date": overall_strategy.todate,
                "entry_time": f"{overall_strategy.entry_time}:00",
                "last_entry_time": f"{overall_strategy.last_entry_time}:00",
                "exit_time": f"{overall_strategy.exit_time}:00",
                "square_off": overall_strategy.square_off,
                "overall_sl": overall_strategy.overall_sl if overall_strategy.overall_sl != 0 else False,
                "overall_target": overall_strategy.overall_target if overall_strategy.overall_target != 0 else False,
                "trailing_for_strategy": False if overall_strategy.profit_reaches == 0 
                else {"trail_type":  overall_strategy.trailing_options, "priceMove":overall_strategy.profit_reaches, "sl_adjustment":overall_strategy.increase_in_profit} 
                if overall_strategy.trailing_options =="lock" 
                else
                    {"trail_type":  "lock_and_trail", "lock_adjustment": {"priceMove":overall_strategy.profit_reaches, "sl_adjustment":overall_strategy.lock_profit, "trail_priceMove": overall_strategy.increase_in_profit, "trail_sl_adjustment": overall_strategy.trail_profit}},
                "implied_futures_expiry": overall_strategy.implied_futures_expiry
            }
            }]
        list_of_legs =[]
        for leg in overall_strategy.legs:
            leg_name = leg.id
            strategy = overall_strategy
            total_lots = leg.lots
            position = leg.position
            option_type = "CE" if leg.option_type=="call" else "PE"
            expiry = leg.expiry
            strike_selection_criteria  = {"strike_selection" : leg.strike_selection_criteria, "value": leg.strike_type} if leg.strike_selection_criteria == "strike" \
            else {"strike_selection" : "closest_premium", "value": leg.closest_premium} if leg.strike_selection_criteria =="closest_premium" \
            else {"strike_selection" : "straddle_width",  "value": {"atm_strike" : leg.straddle_width_sign, "input": leg.straddle_width_value}} if leg.strike_selection_criteria =="straddlewidth"\
            else {"strike_selection" : "atm_pct", "value": {"atm_strike": leg.percent_of_atm_strike_sign, "input": leg.percent_of_atm_strike_value}} if leg.strike_selection_criteria == "percentofatmstrike" \
            else {"strike_selection": "atm_straddle_premium", "value" : leg.atm_straddle_premium }
            roll_strike = False if leg.roll_strike == 0 else {}    
            stop_loss = False if leg.strike_selection_criteria_stop_loss == 0 else [leg.strike_selection_criteria_stop_loss_sign, leg.strike_selection_criteria_stop_loss]
            trailing_sl = False if leg.strike_selection_criteria_profit_reaches == 0 else {"trail_value_type":leg.strike_selection_criteria_lock_profit_sign, "trail_type": "lock", "priceMove": leg.strike_selection_criteria_profit_reaches, "sl_adjustment": leg.strike_selection_criteria_trail_profit} if leg.strike_selection_criteria_trailing_options == "lock" \
             else {"trail_value_type":leg.strike_selection_criteria_lock_profit_sign, "trail_type": "lock_and_trail", "lock_adjustment" : {"priceMove": leg.strike_selection_criteria_profit_reaches, "sl_adjustment": leg.strike_selection_criteria_trail_profit, "trail_priceMove": leg.strike_selection_criteria_increase_in_profit, "trail_sl_adjustment":leg.strike_selection_criteria_trail_profit}}
            no_of_reentry = leg.no_of_reentry
            simple_momentum = False if leg.simple_momentum_range_breakout != "sm" else {"value_type":"points" if leg.simple_momentum_sign =="points" else "percentage", "direction": "increment" if leg.simple_momentum_direction =='+' else "decay"}
            range_breakout = False #need to discuss this point later
            new_strike_selection = False
            leg_detail = {
                "leg_name": leg_name,
                "total_lots": total_lots,
                "position": position,
                "option_type": option_type,
                "expiry": expiry.lower(),
                "strike_selection_criteria": strike_selection_criteria,
                "roll_strike": roll_strike,
                "new_strike_selection": new_strike_selection,
                "stop_loss": stop_loss,
                "trailing_sl": trailing_sl,
                "no_of_reentry": no_of_reentry,
                "simple_momentum": simple_momentum,
                "range_breakout": range_breakout,
            }
            list_of_legs.append(leg_detail)
        payload[0]["legs"]= list_of_legs
        # print(payload)
        for strategy_detail in payload:
            deepak = Strategy(**strategy_detail['strategy_details'])
            print(deepak)
        response = requests.post(url, json=payload)
        # print(response.json())
        return response.json()
        

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
