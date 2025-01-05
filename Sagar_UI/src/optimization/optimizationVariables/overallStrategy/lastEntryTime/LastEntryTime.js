import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./LastEntryTime.css";

const LastEntryTime = (props) => {
  const { min, max, interval, onChangeLastEntryTime } = props;
  return (
    <div className="flex-row last-entry-time-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="time"
            className="form-control"
            id="last_entry_time_min"
            name="last_entry_time_min"
            value={min}
            onChange={(e) =>
              onChangeLastEntryTime("last_entry_time.min", e.target.value)
            }
          ></input>
        </div>
      </div>
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="time"
            className="form-control"
            id="last_entry_time_max"
            name="last_entry_time_max"
            value={max}
            onChange={(e) =>
              onChangeLastEntryTime("last_entry_time.max", e.target.value)
            }
          ></input>
        </div>
      </div>
      <div className="cell interval">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="last_entry_time_interval"
            name="last_entry_time_interval"
            value={interval}
            onChange={(e) =>
              onChangeLastEntryTime("last_entry_time.interval", e.target.value)
            }
            placeholder="minutes"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default LastEntryTime;
