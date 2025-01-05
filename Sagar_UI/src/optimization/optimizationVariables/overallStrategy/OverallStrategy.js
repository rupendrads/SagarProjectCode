import { OptionButtons } from "../../../common/OptionButtons";
import { SelectDD } from "../../../common/SelectDD";
import { InputText } from "../../../common/InputText";
import { Label } from "../../../common/Label";
import "./OverallStrategy.css";
import StrategyType from "./strategyType/StrategyType";
import Underlying from "./underlying/Underlying";
import ImpliedFuturesExpiry from "./impliedFuturesExpiry/ImpliedFuturesExpiry";
import EntryTime from "./entryTime/EntryTime";
import ExitTime from "./exitTime/ExitTime";
import LastEntryTime from "./lastEntryTime/LastEntryTime";
import OverallStopLoss from "./overallStopLoss/OverallStopLoss";
import OverallTarget from "./overallTarget/OverallTarget";
import ProfitReaches from "./profitReaches/ProfitReaches";
import LockProfit from "./lockProfit/LockProfit";
import IncreaseInProfit from "./increaseInProfit/IncreaseInProfit";
import TrailProfit from "./trailProfit/TrailProfit";

const OverallStrategy = (props) => {
  const { optimizationParameters, onChangeOptimizationParameters } = props;
  //console.log("optimizationParameters", optimizationParameters);

  const expiryForImpliedFuturesOptions = [
    {
      value: "current",
      caption: "Current",
    },
    {
      value: "next",
      caption: "Next",
    },
    {
      value: "monthly",
      caption: "Monthly",
    },
  ];

  const trailingOptionsOptions = [
    {
      value: "lock",
      caption: "Lock",
    },
    {
      value: "lockntrail",
      caption: "Lock and Trail",
    },
  ];

  const trailingOptionsCellStyle = {
    marginRight:
      optimizationParameters.trailing_options === "lockntrail" ? "0px" : "20px",
  };

  return (
    <>
      <div className="cell">
        <h6 className="box-title">
          Overall Strategy{" "}
          {optimizationParameters.name && <>({optimizationParameters.name})</>}
        </h6>
        <hr />
      </div>
      <div className="box-content-fill">
        <div className="box card">
          <div className="flex-row strategy-type-row">
            <StrategyType
              strategy_type={optimizationParameters.strategy_type}
            />
            <Underlying underlying={optimizationParameters.underlying} />
            {optimizationParameters.underlying === "impliedfutures" && (
              <ImpliedFuturesExpiry
                implied_futures_expiry={
                  optimizationParameters.implied_futures_expiry
                }
              />
            )}
          </div>
          <div className="flex-row entry-exit-time">
            <div className="cell">
              <div>
                <Label caption="Entry time" />
              </div>
              <EntryTime
                min={optimizationParameters.entry_time.min}
                max={optimizationParameters.entry_time.max}
                interval={optimizationParameters.entry_time.interval}
                onChangeEntryTime={onChangeOptimizationParameters}
              />
            </div>
            <div className="cell">
              <div>
                <Label caption="Exit time" />
              </div>
              <ExitTime
                min={optimizationParameters.exit_time.min}
                max={optimizationParameters.exit_time.max}
                interval={optimizationParameters.exit_time.interval}
                onChangeExitTime={onChangeOptimizationParameters}
              />
            </div>
            <div className="cell">
              <div>
                <Label caption="Last entry time" />
              </div>
              <LastEntryTime
                min={optimizationParameters.last_entry_time.min}
                max={optimizationParameters.last_entry_time.max}
                interval={optimizationParameters.last_entry_time.interval}
                onChangeLastEntryTime={onChangeOptimizationParameters}
              />
              {/* <div className="input-group input-group-sm">
                <input
                  type="time"
                  className="form-control"
                  id="last_entry_time"
                  name="last_entry_time"
                  value={optimizationParameters.last_entry_time}
                  onChange={(e) =>
                    onChangeOptimizationParameters(
                      "last_entry_time",
                      e.target.value
                    )
                  }
                ></input>
              </div> */}
            </div>
          </div>
        </div>
      </div>
      <div className="box-content-fill">
        <div className="box card">
          <div className="flex-row">
            <div className="cell">
              <div>
                <Label caption="Square Off" />
              </div>
              <div disabled>
                <input
                  type="radio"
                  className="btn-check"
                  style={{ padding: "6px" }}
                  name="v_squareOff"
                  id="v_squareOff_complete"
                  autocomplete="off"
                  checked={optimizationParameters.square_off === "complete"}
                  value="complete"
                />
                <label
                  className="btn btn-outline-success rounded-0"
                  for="v_squareOff_complete"
                >
                  Complete
                </label>
                <input
                  type="radio"
                  className="btn-check"
                  style={{ padding: "6px" }}
                  name="v_squareOff"
                  id="v_squareOff_partial"
                  autocomplete="off"
                  checked={optimizationParameters.square_off === "partial"}
                  value="partial"
                />
                <label
                  className="btn btn-outline-success rounded-0"
                  for="v_squareOff_partial"
                >
                  Partial
                </label>
              </div>
            </div>
            <div className="cell">
              <div className="flex-row min-max-interval">
                <div className="cell">
                  <div>
                    <Label caption="Overall Stoploss (+)" />
                  </div>
                  <OverallStopLoss
                    min={optimizationParameters.overall_sl.min}
                    max={optimizationParameters.overall_sl.max}
                    interval={optimizationParameters.overall_sl.interval}
                    onChangeOverallStopLoss={onChangeOptimizationParameters}
                  />
                </div>
              </div>
            </div>
            <div className="cell">
              <div className="flex-row min-max-interval">
                <div className="cell">
                  <div>
                    <Label caption="Overall Target (+)" />
                  </div>
                  <OverallTarget
                    min={optimizationParameters.overall_target.min}
                    max={optimizationParameters.overall_target.max}
                    interval={optimizationParameters.overall_target.interval}
                    onChangeOverallTarget={onChangeOptimizationParameters}
                  />
                </div>
              </div>
            </div>
          </div>
          <div className="flex-row">
            <div className="cell">
              <div>
                <Label caption="Trailing Options" />
              </div>
              <div disabled>
                <select
                  name="v_trailing_options"
                  value={optimizationParameters.trailing_options}
                  className="form-select form-select-sm"
                >
                  {trailingOptionsOptions &&
                    trailingOptionsOptions.map((option) => (
                      <option value={option.value}>{option.caption}</option>
                    ))}
                </select>
              </div>
            </div>
            <div className="cell" style={trailingOptionsCellStyle}>
              <div className="flex-row min-max-interval">
                <div
                  className={`cell ${
                    optimizationParameters.trailing_options === "lockntrail" &&
                    "trailing-options"
                  }`}
                >
                  <div>
                    <Label caption="Profit Reaches (+)" />
                  </div>
                  <ProfitReaches
                    min={optimizationParameters.profit_reaches.min}
                    max={optimizationParameters.profit_reaches.max}
                    interval={optimizationParameters.profit_reaches.interval}
                    onChangeProfitReaches={onChangeOptimizationParameters}
                  />
                </div>
              </div>
            </div>
            <div className="cell" style={trailingOptionsCellStyle}>
              <div className="flex-row min-max-interval">
                <div
                  className={`cell ${
                    optimizationParameters.trailing_options === "lockntrail" &&
                    "trailing-options"
                  }`}
                >
                  <div>
                    <Label caption="Lock Profit (+)" />
                  </div>
                  <LockProfit
                    min={optimizationParameters.lock_profit.min}
                    max={optimizationParameters.lock_profit.max}
                    interval={optimizationParameters.lock_profit.interval}
                    onChangeLockProfit={onChangeOptimizationParameters}
                  />
                </div>
              </div>
            </div>
            {optimizationParameters.trailing_options === "lockntrail" && (
              <>
                <div className="cell" style={trailingOptionsCellStyle}>
                  <div className="flex-row min-max-interval">
                    <div className="cell trailing-options">
                      <div>
                        <Label caption="Increase in Profit (+)" />
                      </div>
                      <IncreaseInProfit
                        min={optimizationParameters.increase_in_profit.min}
                        max={optimizationParameters.increase_in_profit.max}
                        interval={
                          optimizationParameters.increase_in_profit.interval
                        }
                        onChangeIncreaseInProfit={
                          onChangeOptimizationParameters
                        }
                      />
                    </div>
                  </div>
                </div>
                <div className="cell" style={trailingOptionsCellStyle}>
                  <div className="flex-row min-max-interval">
                    <div className="cell trailing-options">
                      <div>
                        <Label caption="Trail Profit (+)" />
                      </div>
                      <TrailProfit
                        min={optimizationParameters.trail_profit.min}
                        max={optimizationParameters.trail_profit.max}
                        interval={optimizationParameters.trail_profit.interval}
                        onChangeTrailProfit={onChangeOptimizationParameters}
                      />
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
};
export default OverallStrategy;
