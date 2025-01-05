import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./RollStrikeProfitReaches.css";

const RollStrikeProfitReaches = (props) => {
  const { min, max, interval, onChangeRollStrikeProfitReaches } = props;

  return (
    <div className="flex-row strike-selection-profit-reaches-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="roll_strike_profit_reaches_min"
            name="roll_strike_profit_reaches_min"
            value={min}
            onChange={(e) =>
              onChangeRollStrikeProfitReaches(
                "roll_strike_profit_reaches.min",
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
            id="roll_strike_profit_reaches_max"
            name="roll_strike_profit_reaches_max"
            value={max}
            onChange={(e) =>
              onChangeRollStrikeProfitReaches(
                "roll_strike_profit_reaches.max",
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
            id="roll_strike_profit_reaches_interval"
            name="roll_strike_profit_reaches_interval"
            value={interval}
            onChange={(e) =>
              onChangeRollStrikeProfitReaches(
                "roll_strike_profit_reaches.interval",
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

export default RollStrikeProfitReaches;
