import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./ProfitReaches.css";

const ProfitReaches = (props) => {
  const { min, max, interval, onChangeProfitReaches } = props;
  return (
    <div className="flex-row profit-reaches-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="profit_reaches_min"
            name="profit_reaches_min"
            value={min}
            onChange={(e) =>
              onChangeProfitReaches("profit_reaches.min", e.target.value)
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
            id="profit_reaches_max"
            name="profit_reaches_max"
            value={max}
            onChange={(e) =>
              onChangeProfitReaches("profit_reaches.max", e.target.value)
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
            id="profit_reaches_interval"
            name="profit_reaches_interval"
            value={interval}
            onChange={(e) =>
              onChangeProfitReaches("profit_reaches.interval", e.target.value)
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default ProfitReaches;
