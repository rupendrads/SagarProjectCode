import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./StraddleWidthValue.css";

const StraddleWidthValue = (props) => {
  const { min, max, interval, onChangeStraddleWidthValue } = props;

  return (
    <div className="flex-row straddle-width-value-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="straddle_width_value_min"
            name="straddle_width_value_min"
            value={min}
            onChange={(e) =>
              onChangeStraddleWidthValue(
                "straddle_width_value.min",
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
            id="straddle_width_value_max"
            name="straddle_width_value_max"
            value={max}
            onChange={(e) =>
              onChangeStraddleWidthValue(
                "straddle_width_value.max",
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
            id="straddle_width_value_interval"
            name="straddle_width_value_interval"
            value={interval}
            onChange={(e) =>
              onChangeStraddleWidthValue(
                "straddle_width_value.interval",
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

export default StraddleWidthValue;
