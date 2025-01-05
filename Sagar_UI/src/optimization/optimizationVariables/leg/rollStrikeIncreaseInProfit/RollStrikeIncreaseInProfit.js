import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./RollStrikeIncreaseInProfit.css";

const RollStrikeIncreaseInProfit = (props) => {
  const { min, max, interval, onChangeRollStrikeIncreaseInProfit } = props;

  return (
    <div className="flex-row roll-strike-increase-in-profit-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="roll_strike_increase_in_profit_min"
            name="roll_strike_increase_in_profit_min"
            value={min}
            onChange={(e) =>
              onChangeRollStrikeIncreaseInProfit(
                "roll_strike_increase_in_profit.min",
                e.target.value
              )
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
            id="roll_strike_increase_in_profit_max"
            name="roll_strike_increase_in_profit_max"
            value={max}
            onChange={(e) =>
              onChangeRollStrikeIncreaseInProfit(
                "roll_strike_increase_in_profit.max",
                e.target.value
              )
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
            id="roll_strike_increase_in_profit_interval"
            name="roll_strike_increase_in_profit_interval"
            value={interval}
            onChange={(e) =>
              onChangeRollStrikeIncreaseInProfit(
                "roll_strike_increase_in_profit.interval",
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

export default RollStrikeIncreaseInProfit;
