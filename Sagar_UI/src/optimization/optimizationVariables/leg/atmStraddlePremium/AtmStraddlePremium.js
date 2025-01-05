import { numberOnly } from "../../../../common/InputValidation";
import "./AtmStraddlePremium.css";

const AtmStraddlePremium = (props) => {
  const { min, max, interval, onChangeAtmStraddlePremium } = props;

  const onChangeMin = (e) => {
    if (e.target.value >= 0 && e.target.value <= 100)
      onChangeAtmStraddlePremium("atm_straddle_premium.min", e.target.value);
  };

  const onChangeMax = (e) => {
    if (e.target.value >= 0 && e.target.value <= 100)
      onChangeAtmStraddlePremium("atm_straddle_premium.max", e.target.value);
  };

  const onChangeInterval = (e) => {
    if (e.target.value >= 0 && e.target.value <= 100)
      onChangeAtmStraddlePremium(
        "atm_straddle_premium.interval",
        e.target.value
      );
  };

  return (
    <div className="flex-row atm-straddle-premium-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={numberOnly}
            id="atm_straddle_premium_min"
            name="atm_straddle_premium_min"
            value={min}
            onChange={onChangeMin}
            placeholder="min"
          ></input>
        </div>
      </div>
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={numberOnly}
            id="atm_straddle_premium_max"
            name="atm_straddle_premium_max"
            value={max}
            onChange={onChangeMax}
            placeholder="max"
          ></input>
        </div>
      </div>
      <div className="cell interval">
        <div className="input-group input-group-sm">
          <input
            type="text"
            min="1"
            max="100"
            className="form-control"
            onKeyDown={numberOnly}
            id="atm_straddle_premium_interval"
            name="atm_straddle_premium_interval"
            value={interval}
            onChange={onChangeInterval}
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default AtmStraddlePremium;
