const Underlying = (props) => {
  const { underlying } = props;

  return (
    <div className="cell">
      <div>
        <label className="field-label">Underlying</label>
      </div>
      <div disabled>
        <input
          type="radio"
          className="btn-check"
          style={{ padding: "6px" }}
          name="v_underlying"
          id="v_underlying_spot"
          autocomplete="off"
          checked={underlying === "spot"}
          value="spot"
        />
        <label
          className="btn btn-outline-success rounded-0"
          for="v_underlying_spot"
        >
          Spot
        </label>
        <input
          type="radio"
          className="btn-check"
          style={{ padding: "6px" }}
          name="v_underlying"
          id="v_underlying_futures"
          autocomplete="off"
          checked={underlying === "futures"}
          value="futures"
        />
        <label
          className="btn btn-outline-success rounded-0"
          for="v_underlying_futures"
        >
          Futures
        </label>
        <input
          type="radio"
          className="btn-check"
          style={{ padding: "6px" }}
          name="v_underlying"
          id="v_underlying_impliedfutures"
          autocomplete="off"
          checked={underlying === "impliedfutures"}
          value="impliedfutures"
        />
        <label
          className="btn btn-outline-success rounded-0"
          for="v_underlying_impliedfutures"
        >
          Implied Futures
        </label>
      </div>
    </div>
  );
};
export default Underlying;
