import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./OverallTarget.css";

const OverallTarget = (props) => {
  const { min, max, interval, onChangeOverallTarget } = props;
  return (
    <div className="flex-row overall-target-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="overall_target_min"
            name="overall_target_min"
            value={min}
            onChange={(e) =>
              onChangeOverallTarget("overall_target.min", e.target.value)
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
            id="overall_target_max"
            name="overall_target_max"
            value={max}
            onChange={(e) =>
              onChangeOverallTarget("overall_target.max", e.target.value)
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
            id="overall_target_interval"
            name="overall_target_interval"
            value={interval}
            onChange={(e) =>
              onChangeOverallTarget("overall_target.interval", e.target.value)
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default OverallTarget;
