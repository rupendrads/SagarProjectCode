import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./StrikeSelectionLockProfit.css";

const StrikeSelectionLockProfit = (props) => {
  const { min, max, interval, onChangeStrikeSelectionLockProfit } = props;

  return (
    <div className="flex-row strike-selection-lock-profit-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="strike_selection_criteria_lock_profit_min"
            name="strike_selection_criteria_lock_profit_min"
            value={min}
            onChange={(e) =>
              onChangeStrikeSelectionLockProfit(
                "strike_selection_criteria_lock_profit.min",
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
            id="strike_selection_criteria_lock_profit_max"
            name="strike_selection_criteria_lock_profit_max"
            value={max}
            onChange={(e) =>
              onChangeStrikeSelectionLockProfit(
                "strike_selection_criteria_lock_profit.max",
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
            id="strike_selection_criteria_lock_profit_interval"
            name="strike_selection_criteria_lock_profit_interval"
            value={interval}
            onChange={(e) =>
              onChangeStrikeSelectionLockProfit(
                "strike_selection_criteria_lock_profit.interval",
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

export default StrikeSelectionLockProfit;
