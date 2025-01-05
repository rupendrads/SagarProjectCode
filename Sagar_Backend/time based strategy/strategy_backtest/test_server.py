from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from Strategy import Strategy
from fastapi.middleware.cors import CORSMiddleware
from LegBuilder import LegBuilder
from utils import read_strategy_folder, process_pnl_files, process_nfo_lot_file, combined_report_generator, analyse_combined_strategy, update_tradebook_with_strategy_pnl
import logging
import json
import asyncio
import warnings
warnings.filterwarnings("ignore")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class LegDetails(BaseModel):
    leg_name: Any
    total_lots: Any
    position: Any
    option_type: Any
    expiry: Any
    strike_selection_criteria: Any
    roll_strike: Any
    new_strike_selection_criteria: Any
    stop_loss: Any
    trailing_sl: Any
    no_of_reentry: Any
    simple_momentum: Any
    range_breakout: Any

class StrategyDetails(BaseModel):
    name: Any
    index: Any
    underlying: Any
    strategy_type: Any
    start_date: Any
    end_date: Any
    entry_time: Any
    last_entry_time: Any
    exit_time: Any
    square_off: Any
    overall_sl: Any
    overall_target: Any
    trailing_for_strategy: Any
    implied_futures_expiry: Any

class StrategyRequest(BaseModel):
    strategy_details: StrategyDetails
    legs: List[LegDetails]

def map_leg_details_to_legbuilder(leg_detail: LegDetails, strategy: Strategy) -> LegBuilder:
    return LegBuilder(
        leg_name=leg_detail.leg_name,
        strategy=strategy,
        total_lots=leg_detail.total_lots,
        position=leg_detail.position,
        option_type=leg_detail.option_type,
        expiry=leg_detail.expiry,
        strike_selection_criteria=leg_detail.strike_selection_criteria,
        roll_strike=leg_detail.roll_strike,
        new_strike_selection_criteria=leg_detail.new_strike_selection_criteria,
        stop_loss=leg_detail.stop_loss,
        trailing_sl=leg_detail.trailing_sl,
        no_of_reentry=leg_detail.no_of_reentry,
        simple_momentum=leg_detail.simple_momentum,
        range_breakout=leg_detail.range_breakout
    )

def map_strategy_details_to_strategy(strategy_details: StrategyDetails) -> Strategy:
    return Strategy(
        name=strategy_details.name,
        index=strategy_details.index,
        underlying=strategy_details.underlying,
        strategy_type=strategy_details.strategy_type,
        start_date=strategy_details.start_date,
        end_date=strategy_details.end_date,
        entry_time=strategy_details.entry_time,
        last_entry_time=strategy_details.last_entry_time,
        exit_time=strategy_details.exit_time,
        square_off=strategy_details.square_off,
        overall_sl=strategy_details.overall_sl,
        overall_target=strategy_details.overall_target,
        trailing_for_strategy=strategy_details.trailing_for_strategy,
        implied_futures_expiry=strategy_details.implied_futures_expiry
    )

@app.post("/run_strategies/")
async def run_strategies(strategy_requests: List[StrategyRequest]):
    try:
        process_nfo_lot_file()
        results = []
        
        for strategy_request in strategy_requests:
            print(strategy_request)
            # Map strategy details to Strategy object
            strategy = map_strategy_details_to_strategy(strategy_request.strategy_details)

            # Map legs to LegBuilder objects
            legs = [map_leg_details_to_legbuilder(leg_detail, strategy) for leg_detail in strategy_request.legs]

            # Run backtests concurrently for all legs
            # tasks = [leg.backtest_selection() for leg in legs]
            # await asyncio.gather(*tasks)

            # Process strategy files (commented out for now)
            # read_strategy_folder(strategy.name, strategy.square_off)
            # process_pnl_files(strategy.name, strategy.overall_target, -strategy.overall_sl, strategy.square_off)
            # analyse_combined_strategy(strategy.name)
            # response = combined_report_generator(strategy)
            # update_tradebook_with_strategy_pnl(strategy)

            # Uncomment and handle response
            # if response:
            #     results.append({
            #         "status": "success",
            #         "message": f"Strategy {strategy.name} executed successfully",
            #         "data": json.loads(response)
            #     })
            # else:
            #     results.append({
            #         "status": "failure",
            #         "message": f"Strategy {strategy.name} failed to generate a report"
            #     })
        
        return None #results

    except Exception as e:
        logging.exception("Error occurred while running strategies")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
