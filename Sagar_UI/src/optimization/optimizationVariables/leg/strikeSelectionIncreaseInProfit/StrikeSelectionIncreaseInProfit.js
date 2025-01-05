import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./StrikeSelectionIncreaseInProfit.css";

const StrikeSelectionIncreaseInProfit = (props) => {
  const { min, max, interval, onChangeStrikeSelectionIncreaseInProfit } = props;

  return (
    <div className="flex-row strike-selection-increase-in-profit-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="strike_selection_criteria_increase_in_profit_min"
            name="strike_selection_criteria_increase_in_profit_min"
            value={min}
            onChange={(e) =>
              onChangeStrikeSelectionIncreaseInProfit(
                "strike_selection_criteria_increase_in_profit.min",
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
            id="strike_selection_criteria_increase_in_profit_max"
            name="strike_selection_criteria_increase_in_profit_max"
            value={max}
            onChange={(e) =>
              onChangeStrikeSelectionIncreaseInProfit(
                "strike_selection_criteria_increase_in_profit.max",
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
            id="strike_selection_criteria_increase_in_profit_interval"
            name="strike_selection_criteria_increase_in_profit_interval"
            value={interval}
            onChange={(e) =>
              onChangeStrikeSelectionIncreaseInProfit(
                "strike_selection_criteria_increase_in_profit.interval",
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

export default StrikeSelectionIncreaseInProfit;
