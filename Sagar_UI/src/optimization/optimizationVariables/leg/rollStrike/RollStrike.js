import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./RollStrike.css";

const RollStrike = (props) => {
  const { min, max, interval, onChangeRollStrike } = props;

  return (
    <div className="flex-row roll-strike-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="roll_strike_min"
            name="roll_strike_min"
            value={min}
            onChange={(e) =>
              onChangeRollStrike("roll_strike.min", e.target.value)
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
            id="roll_strike_max"
            name="roll_strike_max"
            value={max}
            onChange={(e) =>
              onChangeRollStrike("roll_strike.max", e.target.value)
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
            id="roll_strike_interval"
            name="roll_strike_interval"
            value={interval}
            onChange={(e) =>
              onChangeRollStrike("roll_strike.interval", e.target.value)
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default RollStrike;
