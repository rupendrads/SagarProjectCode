const StrategyType = (props) => {
  const { strategy_type } = props;
  return (
    <div className="cell">
      <div>
        <label className="field-label">Strategy Type</label>
      </div>
      <div disabled>
        <input
          type="radio"
          className="btn-check"
          style={{ padding: "6px" }}
          name="v_strategyType"
          id="v_strategyType_intraday"
          autocomplete="off"
          checked={strategy_type === "intraday"}
          value="intraday"
        />
        <label
          className="btn btn-outline-success rounded-0"
          for="v_strategyType_intraday"
        >
          Intraday
        </label>
        <input
          type="radio"
          className="btn-check"
          style={{ padding: "6px" }}
          name="v_strategyType"
          id="v_strategyType_btst"
          autocomplete="off"
          checked={strategy_type === "btst"}
          value="btst"
        />
        <label
          className="btn btn-outline-success rounded-0"
          for="v_strategyType_btst"
        >
          BTST
        </label>
        <input
          type="radio"
          className="btn-check"
          style={{ padding: "6px" }}
          name="v_strategyType"
          id="v_strategyType_positional"
          autocomplete="off"
          checked={strategy_type === "positional"}
          value="positional"
        />
        <label
          className="btn btn-outline-success rounded-0"
          for="v_strategyType_positional"
        >
          Positional
        </label>
      </div>
    </div>
  );
};

export default StrategyType;
