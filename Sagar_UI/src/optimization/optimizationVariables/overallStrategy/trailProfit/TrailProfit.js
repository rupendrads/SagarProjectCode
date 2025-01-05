import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./TrailProfit.css";

const TrailProfit = (props) => {
  const { min, max, interval, onChangeTrailProfit } = props;

  return (
    <div className="flex-row trail-profit-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="trail_profit_min"
            name="trail_profit_min"
            value={min}
            onChange={(e) =>
              onChangeTrailProfit("trail_profit.min", e.target.value)
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
            id="trail_profit_max"
            name="trail_profit_max"
            value={max}
            onChange={(e) =>
              onChangeTrailProfit("trail_profit.max", e.target.value)
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
            id="trail_profit_interval"
            name="trail_profit_interval"
            value={interval}
            onChange={(e) =>
              onChangeTrailProfit("trail_profit.interval", e.target.value)
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default TrailProfit;
