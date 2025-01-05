import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./StrikeSelectionStopLoss.css";

const StrikeSelectionStopLoss = (props) => {
  const { min, max, interval, onChangeStrikeSelectionStopLoss } = props;
  return (
    <div className="flex-row strike-selection-stop-loss-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="strike_selection_criteria_stop_loss_min"
            name="strike_selection_criteria_stop_loss_min"
            value={min}
            onChange={(e) =>
              onChangeStrikeSelectionStopLoss(
                "strike_selection_criteria_stop_loss.min",
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
            id="strike_selection_criteria_stop_loss_max"
            name="strike_selection_criteria_stop_loss_max"
            value={max}
            onChange={(e) =>
              onChangeStrikeSelectionStopLoss(
                "strike_selection_criteria_stop_loss.max",
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
            id="strike_selection_criteria_stop_loss_interval"
            name="strike_selection_criteria_stop_loss_interval"
            value={interval}
            onChange={(e) =>
              onChangeStrikeSelectionStopLoss(
                "strike_selection_criteria_stop_loss.interval",
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
export default StrikeSelectionStopLoss;
