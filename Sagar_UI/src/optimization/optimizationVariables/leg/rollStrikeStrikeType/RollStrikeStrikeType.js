import { positiveNumberOnly } from "../../../../common/InputValidation";
import { numberOnly } from "../../../../common/InputValidation";
import "./RollStrikeStrikeType.css";

const RollStrikeStrikeType = (props) => {
  const { min, max, interval, onChangeRollStrikeStrikeType } = props;

  const onChangeMin = (e) => {
    if ((e.target.value >= -10 && e.target.value <= 9) || e.target.value == "-")
      onChangeRollStrikeStrikeType(
        "roll_strike_strike_type.min",
        e.target.value
      );
  };

  const onChangeMax = (e) => {
    if ((e.target.value >= -9 && e.target.value <= 10) || e.target.value == "-")
      onChangeRollStrikeStrikeType(
        "roll_strike_strike_type.max",
        e.target.value
      );
  };

  const onChangeInterval = (e) => {
    onChangeRollStrikeStrikeType(
      "roll_strike_strike_type.interval",
      e.target.value
    );
  };

  return (
    <div className="flex-row roll-strike-strike-type-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={numberOnly}
            id="roll_strike_strike_type_min"
            name="roll_strike_strike_type_min"
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
            id="roll_strike_strike_type_max"
            name="roll_strike_strike_type_max"
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
            id="roll_strike_strike_type_interval"
            name="roll_strike_strike_type_interval"
            value={interval}
            onChange={onChangeInterval}
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default RollStrikeStrikeType;
