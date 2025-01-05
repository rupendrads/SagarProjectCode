import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./RollStrikeTrailProfit.css";

const RollStrikeTrailProfit = (props) => {
  const { min, max, interval, onChangeRollStrikeTrailProfit } = props;

  return (
    <div className="flex-row roll-strike-trail-profit-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="roll_strike_trail_profit_min"
            name="roll_strike_trail_profit_min"
            value={min}
            onChange={(e) =>
              onChangeRollStrikeTrailProfit(
                "roll_strike_trail_profit.min",
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
            id="roll_strike_trail_profit_max"
            name="roll_strike_trail_profit_max"
            value={max}
            onChange={(e) =>
              onChangeRollStrikeTrailProfit(
                "roll_strike_trail_profit.max",
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
            id="roll_strike_trail_profit_interval"
            name="roll_strike_trail_profit_interval"
            value={interval}
            onChange={(e) =>
              onChangeRollStrikeTrailProfit(
                "roll_strike_trail_profit.interval",
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

export default RollStrikeTrailProfit;
