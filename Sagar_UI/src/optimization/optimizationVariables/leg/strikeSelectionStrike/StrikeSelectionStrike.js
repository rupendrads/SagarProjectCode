import {
  numberOnly,
  positiveNumberOnly,
} from "../../../../common/InputValidation";
import "./StrikeSelectionStrike.css";

const StrikeSelectionStrike = (props) => {
  const { min, max, interval, onChangeStrikeSelectionStrike } = props;

  const onChangeMin = (e) => {
    if (
      (e.target.value >= -20 && e.target.value <= 19) ||
      e.target.value == "-"
    )
      onChangeStrikeSelectionStrike("strike_type.min", e.target.value);
  };

  const onChangeMax = (e) => {
    if (
      (e.target.value >= -19 && e.target.value <= 20) ||
      e.target.value == "-"
    )
      onChangeStrikeSelectionStrike("strike_type.max", e.target.value);
  };

  const onChangeInterval = (e) => {
    onChangeStrikeSelectionStrike("strike_type.interval", e.target.value);
  };

  return (
    <div className="flex-row strike-selection-strike-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={numberOnly}
            id="strike_type_min"
            name="strike_type_min"
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
            id="strike_type_max"
            name="strike_type_max"
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
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="strike_type_interval"
            name="strike_type_interval"
            value={interval}
            onChange={onChangeInterval}
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default StrikeSelectionStrike;
