import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./ExitTime.css";

const ExitTime = (props) => {
  const { min, max, interval, onChangeExitTime } = props;
  return (
    <div className="flex-row exit-time-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="time"
            className="form-control"
            id="exit_time_min"
            name="exit_time_min"
            value={min}
            onChange={(e) => onChangeExitTime("exit_time.min", e.target.value)}
          ></input>
        </div>
      </div>
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="time"
            className="form-control"
            id="exit_time_max"
            name="exit_time_max"
            value={max}
            onChange={(e) => onChangeExitTime("exit_time.max", e.target.value)}
          ></input>
        </div>
      </div>
      <div className="cell interval">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="exit_time_interval"
            name="exit_time_interval"
            value={interval}
            onChange={(e) =>
              onChangeExitTime("exit_time.interval", e.target.value)
            }
            placeholder="minutes"
          ></input>
        </div>
      </div>
    </div>
  );
};
export default ExitTime;
