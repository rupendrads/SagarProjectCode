import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./StrikeSelectionTrailProfit.css";

const StrikeSelectionTrailProfit = (props) => {
  const { min, max, interval, onChangeStrikeSelectionTrailProfit } = props;

  return (
    <div className="flex-row strike-selection-trail-profit-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="strike_selection_criteria_trail_profit_min"
            name="strike_selection_criteria_trail_profit_min"
            value={min}
            onChange={(e) =>
              onChangeStrikeSelectionTrailProfit(
                "strike_selection_criteria_trail_profit.min",
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
            id="strike_selection_criteria_trail_profit_max"
            name="strike_selection_criteria_trail_profit_max"
            value={max}
            onChange={(e) =>
              onChangeStrikeSelectionTrailProfit(
                "strike_selection_criteria_trail_profit.max",
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
            id="strike_selection_criteria_trail_profit_interval"
            name="strike_selection_criteria_trail_profit_interval"
            value={interval}
            onChange={(e) =>
              onChangeStrikeSelectionTrailProfit(
                "strike_selection_criteria_trail_profit.interval",
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

export default StrikeSelectionTrailProfit;
