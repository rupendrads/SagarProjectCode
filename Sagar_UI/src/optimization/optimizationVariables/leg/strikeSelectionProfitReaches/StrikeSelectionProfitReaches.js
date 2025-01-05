import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./StrikeSelectionProfitReaches.css";

const StrikeSelectionProfitReaches = (props) => {
  const { min, max, interval, onChangeStrikeSelectionProfitReaches } = props;
  return (
    <div className="flex-row strike-selection-profit-reaches-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="strike_selection_criteria_profit_reaches_min"
            name="strike_selection_criteria_profit_reaches_min"
            value={min}
            onChange={(e) =>
              onChangeStrikeSelectionProfitReaches(
                "strike_selection_criteria_profit_reaches.min",
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
            id="strike_selection_criteria_profit_reaches_max"
            name="strike_selection_criteria_profit_reaches_max"
            value={max}
            onChange={(e) =>
              onChangeStrikeSelectionProfitReaches(
                "strike_selection_criteria_profit_reaches.max",
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
            id="strike_selection_criteria_profit_reaches_interval"
            name="strike_selection_criteria_profit_reaches_interval"
            value={interval}
            onChange={(e) =>
              onChangeStrikeSelectionProfitReaches(
                "strike_selection_criteria_profit_reaches.interval",
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

export default StrikeSelectionProfitReaches;
