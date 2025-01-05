import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./NoOfReentry.css";

const NoOfReentry = (props) => {
  const { min, max, interval, onChangeNoOfReentry } = props;
  return (
    <div className="flex-row no-of-reentry-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="no_of_reentry_min"
            name="no_of_reentry_min"
            value={min}
            onChange={(e) =>
              onChangeNoOfReentry("no_of_reentry.min", e.target.value)
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
            id="no_of_reentry_max"
            name="no_of_reentry_max"
            value={max}
            onChange={(e) =>
              onChangeNoOfReentry("no_of_reentry.max", e.target.value)
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
            id="no_of_reentry_interval"
            name="no_of_reentry_interval"
            value={interval}
            onChange={(e) =>
              onChangeNoOfReentry("no_of_reentry.interval", e.target.value)
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default NoOfReentry;
