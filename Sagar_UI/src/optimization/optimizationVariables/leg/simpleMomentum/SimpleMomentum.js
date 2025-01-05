import { positiveNumberOnly } from "../../../../common/InputValidation";
import "./SimpleMomentum.css";

const SimpleMomentum = (props) => {
  const { min, max, interval, onChangeSimpleMomentum } = props;

  return (
    <div className="flex-row simple-momentum-min-max-interval-cell">
      <div className="cell">
        <div className="input-group input-group-sm">
          <input
            type="text"
            className="form-control"
            onKeyDown={positiveNumberOnly}
            id="simple_momentum_min"
            name="simple_momentum_min"
            value={min}
            onChange={(e) =>
              onChangeSimpleMomentum("simple_momentum.min", e.target.value)
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
            id="simple_momentum_max"
            name="simple_momentum_max"
            value={max}
            onChange={(e) =>
              onChangeSimpleMomentum("simple_momentum.max", e.target.value)
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
            id="simple_momentum_interval"
            name="simple_momentum_interval"
            value={interval}
            onChange={(e) =>
              onChangeSimpleMomentum("simple_momentum.interval", e.target.value)
            }
            placeholder="interval"
          ></input>
        </div>
      </div>
    </div>
  );
};

export default SimpleMomentum;
