import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./OverallStopLoss.css";

const OverallStopLoss = (props) => {
  const { min, max, interval, onChangeOverallStopLoss } = props;
  return (
    <div className="flex-row overall-stoploss-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="overall_sl_min"
            name="overall_sl_min"
            value={min}
            onChange={(e) =>
              onChangeOverallStopLoss("overall_sl.min", e.target.value)
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
            id="overall_sl_max"
            name="overall_sl_max"
            value={max}
            onChange={(e) =>
              onChangeOverallStopLoss("overall_sl.max", e.target.value)
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
            id="overall_sl_interval"
            name="overall_sl_interval"
            value={interval}
            onChange={(e) =>
              onChangeOverallStopLoss("overall_sl.interval", e.target.value)
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default OverallStopLoss;
