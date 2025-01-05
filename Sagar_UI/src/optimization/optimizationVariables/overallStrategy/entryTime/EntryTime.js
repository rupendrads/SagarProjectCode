import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./EntryTime.css";

const EntryTime = (props) => {
  const { min, max, interval, onChangeEntryTime } = props;
  return (
    <div className="flex-row entry-time-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="time"
            className="form-control"
            id="entry_time_min"
            name="entry_time_min"
            value={min}
            onChange={(e) =>
              onChangeEntryTime("entry_time.min", e.target.value)
            }
          ></input>
        </div>
      </div>
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="time"
            className="form-control"
            id="entry_time_max"
            name="entry_time_max"
            value={max}
            onChange={(e) =>
              onChangeEntryTime("entry_time.max", e.target.value)
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
            id="entry_time_interval"
            name="entry_time_interval"
            value={interval}
            onChange={(e) =>
              onChangeEntryTime("entry_time.interval", e.target.value)
            }
            placeholder="minutes"
          ></input>
        </div>
      </div>
    </div>
  );
};
export default EntryTime;
