import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./LockProfit.css";

const LockProfit = (props) => {
  const { min, max, interval, onChangeLockProfit } = props;
  return (
    <div className="flex-row lock-profit-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="lock_profit_min"
            name="lock_profit_min"
            value={min}
            onChange={(e) =>
              onChangeLockProfit("lock_profit.min", e.target.value)
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
            id="lock_profit_max"
            name="lock_profit_max"
            value={max}
            onChange={(e) =>
              onChangeLockProfit("lock_profit.max", e.target.value)
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
            id="lock_profit_interval"
            name="lock_profit_interval"
            value={interval}
            onChange={(e) =>
              onChangeLockProfit("lock_profit.interval", e.target.value)
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default LockProfit;
