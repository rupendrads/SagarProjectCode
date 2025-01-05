from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from Strategy import Strategy
from LegBuilder import LegBuilder
from utils import   convert_numpy_types, assign_index, read_strategy_folder, process_pnl_files, process_nfo_lot_file, combined_report_generator, analyse_combined_strategy, update_tradebook_with_strategy_pnl,analyze_tradebook, update_tradebook_with_pnl, process_strategy_constraints
import logging
import os
import gzip
import shutil
from datetime import datetime, timedelta
import glob
import pandas as pd
import json
import asyncio
import warnings
from fastapi.middleware.cors import CORSMiddleware
import time
import random
from data import get_expiry_df, get_underlying_ltp
warnings.filterwarnings("ignore")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")



class LegDetails(BaseModel):
    leg_name: str
    total_lots: int
    position: str
    option_type: str
    expiry: str
    strike_selection_criteria: Dict[str, Any]
    roll_strike: Any
    new_strike_selection_criteria: Any
    stop_loss: List[Any]
    trailing_sl: Any
    no_of_reentry: int
    simple_momentum: Any
    range_breakout: Any

class StrategyDetails(BaseModel):
    name: str
    index: str
    underlying: str
    strategy_type: str
    start_date: str
    end_date: str
    entry_time: str
    last_entry_time: str
    exit_time: str
    square_off: Any
    overall_sl: Any
    overall_target: Any
    trailing_for_strategy: Any
    implied_futures_expiry: Any
    optimization_flag: bool
    brokerage: Optional[int]=20
class StrategyRequest(BaseModel):
    strategy_details: StrategyDetails
    legs: List[LegDetails]

@app.post("/run_strategies/")
async def run_strategies(strategy_requests: List[StrategyRequest]):
    print("----------------------------------------------------------------------------")
    print(strategy_requests)
    print("----------------------------------------------------------------------------")
    
    try:
        # print(strategy_requests[0].strategy_details)
        strategy_requests[0].strategy_details.index = assign_index(strategy_requests[0].strategy_details.index)
        implied_futures_expiry = 0 if strategy_requests[0].strategy_details.implied_futures_expiry.lower() == 'current' else 1 if strategy_requests[0].strategy_details.implied_futures_expiry.lower() == 'next' else False
        print(f"--------------{implied_futures_expiry} is implied_futures_expiry------------------------")
        fut_data = get_underlying_ltp(strategy_requests[0].strategy_details.index, strategy_requests[0].strategy_details.start_date, strategy_requests[0].strategy_details.end_date, strategy_requests[0].strategy_details.underlying, strategy_requests[0].strategy_details.implied_futures_expiry)
        print(f"-------------------------futures data---------------------------")
        print(fut_data.head())
        options_data = get_expiry_df(strategy_requests[0].strategy_details.index, strategy_requests[0].strategy_details.start_date, strategy_requests[0].strategy_details.end_date, "09:15:00", "15:30:00")
        # # fut_data = get_underlying_ltp(strategy_requests[0].index, strategy_requests[0].entry_time, strategy_requests[0].start_date, strategy_requests[0].end_date,strategy_requests[0].underlying, implied_futures_expiry)
        print(f"-----------------options data retrieved outside strategy class --------------------")
        # strategy_requests[0].underlying_data = fut_data
        # strategy_details[0].options_data = options_data
        # print(strategy_details)
        # print(options_data.head())
        process_nfo_lot_file()                  
        results = []
        # if os.path.exists(strategy.name):
        #     shutil.rmtree(strategy.name)
        #     print(f"Deleted existing folder: {strategy.name}")
        #  data is here, is 
        for strategy_request in strategy_requests:
            strategy_details = strategy_request.strategy_details.dict()
            print(f"--------strategy details----------")
            strategy_details["underlying_data"]= fut_data
            strategy_details["options_data"] = options_data
            # strategy_details["optimization_flag"] = optimization_flag
            strategy = Strategy(**strategy_details)
            
            legs = []
            for leg_detail in strategy_request.legs:
                leg = LegBuilder(
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
                legs.append(leg)
            # os.makedirs(strategy.name)
            tasks = [leg.backtest_selection() for leg in legs]
            await asyncio.gather(*tasks)

            read_strategy_folder(strategy.name, strategy.square_off)
            process_pnl_files(strategy)
            process_strategy_constraints(strategy)
            analyse_combined_strategy(strategy.name)
            # OverallPerformance = combined_report_generator(strategy)
            combined_report_generator(strategy)
            tradebook = update_tradebook_with_strategy_pnl(strategy)
            tradebook = update_tradebook_with_pnl(tradebook, strategy)    
            os.makedirs(strategy.name, exist_ok=True)
            tradebook.to_csv(os.path.join(strategy.name, f"{strategy.name}_combined_tradebook.csv"), index=False)
            OverallPerformance = analyze_tradebook(strategy)
            result = []
            tradebook['tsl']= tradebook['tsl'].fillna('nan') #testing for no tsl case
            for index, row in tradebook.iterrows():
                result.append({
                    "symbol": row['symbol'],
                    "trade": row['trade'].upper(),
                    "entry_time": row['entry_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    "entry_price": row['entry_price'],
                    "exit_time": row['exit_time'],
                    "exit_price": row['exit_price'],
                    "sl": row['sl'],
                    "tsl": row['tsl'],
                    "qty": row['qty'],
                    "pnl": row['pnl'],
                    "maxLossStrategy": row['maxLossStrategy'],
                    "maxProfitStrategy": row['maxProfitStrategy'],
                    "futureEntry": row['futureEntry'],
                    "futureExit": row['futureExit'],
                    "comment": row['comment']
                })
           
            # print(result)
            print(f"---------------------response--------------------")
            # print(OverallPerformance)
            if  strategy.optimization_flag:
                print(OverallPerformance)
                print(f"strategy optimizer is {strategy.optimization_flag}")
                newOverallPerformance = OverallPerformance #convert_numpy_types(OverallPerformance)
                response = {
                    "netProfit" : (newOverallPerformance["TotalProfit"]),
                    "winningTrades": newOverallPerformance["DaysProfit"],
                    "losingTrades": newOverallPerformance["DaysLoss"],
                    "winningStrike": newOverallPerformance["MaxWinningStreak"],
                    "losingStrike": newOverallPerformance["MaxLosingStreak"],
                    "expenctancy" : newOverallPerformance["ExpectancyRatio"],
                    "averageProfit" : newOverallPerformance["AverageProfit"],
                    "averageLoss" : newOverallPerformance["AverageLoss"],
                    "maxDrawDown" : newOverallPerformance["MaxDrawdown" ],
                    "maxDrawDownDuration" : newOverallPerformance["DurationOfMaxDrawdown"]["days"],
                    "systemDrawdown": "0",
                    "parameters": {},#{"strategy_parameters": strategy_details, "legs":legs },
                    "numberOfTrades": len(tradebook),
                    "totalBrokerage": {}


                }
                print(response)
                return response
            overall_performance_df = pd.DataFrame(OverallPerformance)
            overall_performance_df.to_csv(f'{strategy.name}/{strategy.name}_OverallPerformance.csv',index=False)
            print(f"overall perfomance saved")
            response = {
                # "TaxAndCharges": {
                #     "ClearingCharges": 20,
                #     "IPFT": 20,
                #     "STT": 10,
                #     "StampDuty": 20,
                #     "SEBICharges": 30.2,
                #     "ExchangeCharges": 20,
                #     "GST": 36,
                #     "Total": 136.2
                # },
                "OverallPerformance": OverallPerformance,
                "YearlyData": []
            }
            yearly_data = {}
            for _, trade in tradebook.iterrows():
                year = pd.to_datetime(trade['entry_time']).year
                month = pd.to_datetime(trade['entry_time']).strftime('%b')
                pnl = round(trade['pnl'], 2)

                if year not in yearly_data:
                    yearly_data[year] = {
                        "Year": year,
                        "MonthlyPerformance": {month: 0 for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']},
                        "Total": 0,
                        "CumulativePnL": [],
                        "Dates": []
                    }
                
                yearly_data[year]["MonthlyPerformance"][month] = round(yearly_data[year]["MonthlyPerformance"][month] + pnl, 2)
                yearly_data[year]["Total"] = round(yearly_data[year]["Total"] + pnl, 2)
                yearly_data[year]["CumulativePnL"].append(round(yearly_data[year]["Total"], 2))
                yearly_data[year]["Dates"].append(pd.to_datetime(trade['entry_time']))

            for year, year_data in yearly_data.items():
                cumulative_pnl = year_data["CumulativePnL"]
                dates = year_data["Dates"]
                
                max_drawdown = 0
                max_drawdown_duration = timedelta(0)
                max_drawdown_start = None
                max_drawdown_end = None
                peak = cumulative_pnl[0]
                
                for i in range(1, len(cumulative_pnl)):
                    if cumulative_pnl[i] > peak:
                        peak = cumulative_pnl[i]
                    drawdown = round(peak - cumulative_pnl[i], 2)
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                        max_drawdown_end = dates[i]
                        for j in range(i, -1, -1):
                            if cumulative_pnl[j] == peak:
                                max_drawdown_start = dates[j]
                                break
                        max_drawdown_duration = max_drawdown_end - max_drawdown_start

                year_data["MaxDrawdown"] = OverallPerformance["MaxDrawdown"]#round(max_drawdown, 2)
                year_data["DaysForMaxDrawdown"] = OverallPerformance["DurationOfMaxDrawdown"]["days"]#max_drawdown_duration.days
                year_data["DurationOfMaxDrawdown"] = {
                    "start": OverallPerformance["DurationOfMaxDrawdown"]["start"].strftime("%d/%m/%Y") if OverallPerformance["DurationOfMaxDrawdown"]["start"] else None,
                    "end": OverallPerformance["DurationOfMaxDrawdown"]["end"].strftime("%d/%m/%Y") if OverallPerformance["DurationOfMaxDrawdown"]["end"] else None
                }
                try:
                    year_data["ReturnToMaxDDYearly"] = round((year_data["Total"] / OverallPerformance["MaxDrawdown"]) * 100, 2) if max_drawdown != 0 else 0
                except:
                    year_data["ReturnToMaxDDYearly"] = 0

                del year_data["CumulativePnL"]
                del year_data["Dates"]

                response["YearlyData"].append(year_data)

            response["YearlyData"].sort(key=lambda x: x["Year"])
            response["tradebook"] = result
            # if response:
            #     return response
            # else:
            #     results.append({"status": "failure", "message": f"Strategy {strategy.name} failed to generate a report"})
        print("\n \n \n")
        # print(json.dumps(response, indent=4, default=str))
        # print(response['OverallPerformance'])
        try:
            # print(response)
            return response 
        except Exception as e:
            print(f"error while returning is {e}")

    except Exception as e:
        logging.exception("Error occurred while running strategies")
        print("Error occurred while running strategies")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
