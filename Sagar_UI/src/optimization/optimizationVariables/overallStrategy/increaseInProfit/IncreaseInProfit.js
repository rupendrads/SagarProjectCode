import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./IncreaseInProfit.css";

const IncreaseInProfit = (props) => {
  const { min, max, interval, onChangeIncreaseInProfit } = props;
  return (
    <div className="flex-row increase-in-profit-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="increase_in_profit_min"
            name="increase_in_profit_min"
            value={min}
            onChange={(e) =>
              onChangeIncreaseInProfit("increase_in_profit.min", e.target.value)
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
            id="increase_in_profit_max"
            name="increase_in_profit_max"
            value={max}
            onChange={(e) =>
              onChangeIncreaseInProfit("increase_in_profit.max", e.target.value)
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
            id="increase_in_profit_interval"
            name="increase_in_profit_interval"
            value={interval}
            onChange={(e) =>
              onChangeIncreaseInProfit(
                "increase_in_profit.interval",
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

export default IncreaseInProfit;
