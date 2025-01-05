import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./PercentOfAtmStrikeValue.css";

const PercentOfAtmStrikeValue = (props) => {
  const { min, max, interval, onChangePercentOfAtmStrikeValue } = props;

  return (
    <div className="flex-row percent-of-atm-strike-value-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="percent_of_atm_strike_value_min"
            name="percent_of_atm_strike_value_min"
            value={min}
            onChange={(e) =>
              onChangePercentOfAtmStrikeValue(
                "percent_of_atm_strike_value.min",
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
            id="percent_of_atm_strike_value_max"
            name="percent_of_atm_strike_value_max"
            value={max}
            onChange={(e) =>
              onChangePercentOfAtmStrikeValue(
                "percent_of_atm_strike_value.max",
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
            id="percent_of_atm_strike_value_interval"
            name="percent_of_atm_strike_value_interval"
            value={interval}
            onChange={(e) =>
              onChangePercentOfAtmStrikeValue(
                "percent_of_atm_strike_value.interval",
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

export default PercentOfAtmStrikeValue;
