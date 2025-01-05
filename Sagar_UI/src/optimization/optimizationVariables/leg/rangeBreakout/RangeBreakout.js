import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./RangeBreakout.css";

const RangeBreakout = (props) => {
  const { min, max, interval, onChangeRangeBreakout } = props;

  return (
    <div className="flex-row range-breakout-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="range_breakout_min"
            name="range_breakout_min"
            value={min}
            onChange={(e) =>
              onChangeRangeBreakout("range_breakout.min", e.target.value)
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
            id="range_breakout_max"
            name="range_breakout_max"
            value={max}
            onChange={(e) =>
              onChangeRangeBreakout("range_breakout.max", e.target.value)
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
            id="range_breakout_interval"
            name="range_breakout_interval"
            value={interval}
            onChange={(e) =>
              onChangeRangeBreakout("range_breakout.interval", e.target.value)
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default RangeBreakout;
