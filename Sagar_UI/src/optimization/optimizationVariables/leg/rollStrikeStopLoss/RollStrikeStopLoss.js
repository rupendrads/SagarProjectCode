import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./RollStrikeStopLoss.css";

const RollStrikeStopLoss = (props) => {
  const { min, max, interval, onChangeRollStrikeStopLoss } = props;

  return (
    <div className="flex-row roll-strike-stop-loss-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="roll_strike_stop_loss_min"
            name="roll_strike_stop_loss_min"
            value={min}
            onChange={(e) =>
              onChangeRollStrikeStopLoss(
                "roll_strike_stop_loss.min",
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
            id="roll_strike_stop_loss_max"
            name="roll_strike_stop_loss_max"
            value={max}
            onChange={(e) =>
              onChangeRollStrikeStopLoss(
                "roll_strike_stop_loss.max",
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
            id="roll_strike_stop_loss_interval"
            name="roll_strike_stop_loss_interval"
            value={interval}
            onChange={(e) =>
              onChangeRollStrikeStopLoss(
                "roll_strike_stop_loss.interval",
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

export default RollStrikeStopLoss;
