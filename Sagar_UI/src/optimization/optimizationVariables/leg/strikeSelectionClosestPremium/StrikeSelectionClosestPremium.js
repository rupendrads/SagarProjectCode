import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./StrikeSelectionClosestPremium.css";

const StrikeSelectionClosestPremium = (props) => {
  const { min, max, interval, onChangeStrikeSelectionClosestPremium } = props;

  return (
    <div className="flex-row strike-selection-closest-premium-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="closest_premium_min"
            name="closest_premium_min"
            value={min}
            onChange={(e) =>
              onChangeStrikeSelectionClosestPremium(
                "closest_premium.min",
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
            id="closest_premium_max"
            name="closest_premium_max"
            value={max}
            onChange={(e) =>
              onChangeStrikeSelectionClosestPremium(
                "closest_premium.max",
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
            id="closest_premium_interval"
            name="closest_premium_interval"
            value={interval}
            onChange={(e) =>
              onChangeStrikeSelectionClosestPremium(
                "closest_premium.interval",
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

export default StrikeSelectionClosestPremium;
