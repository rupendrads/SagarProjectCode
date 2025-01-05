import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./RollStrikeLockProfit.css";

const RollStrikeLockProfit = (props) => {
  const { min, max, interval, onChangeRollStrikeLockProfit } = props;

  return (
    <div className="flex-row roll-strike-lock-profit-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="roll_strike_lock_profit_min"
            name="roll_strike_lock_profit_min"
            value={min}
            onChange={(e) =>
              onChangeRollStrikeLockProfit(
                "roll_strike_lock_profit.min",
                e.target.value
              )
            }
            placeholder="min"
          ></input>
        </div>
      </div>
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="roll_strike_lock_profit_max"
            name="roll_strike_lock_profit_max"
            value={max}
            onChange={(e) =>
              onChangeRollStrikeLockProfit(
                "roll_strike_lock_profit.max",
                e.target.value
              )
            }
            placeholder="max"
          ></input>
        </div>
      </div>
      <div className="cell interval">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="roll_strike_lock_profit_interval"
            name="roll_strike_lock_profit_interval"
            value={interval}
            onChange={(e) =>
              onChangeRollStrikeLockProfit(
                "roll_strike_lock_profit.interval",
                e.target.value
              )
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default RollStrikeLockProfit;
