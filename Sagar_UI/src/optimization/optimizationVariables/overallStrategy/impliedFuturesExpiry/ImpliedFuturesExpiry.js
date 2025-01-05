const ImpliedFuturesExpiry = (props) => {
  const { implied_futures_expiry } = props;

  const options = [
    {
      value: "current",
      caption: "Current",
    },
    {
      value: "next",
      caption: "Next",
    },
    {
      value: "monthly",
      caption: "Monthly",
    },
  ];

  return (
    <div className="cell">
      <div>
        <label className="field-label">Implied Futures Expiry</label>
      </div>
      <div disabled>
        <select
          name="implied_futures_expiry"
          value={implied_futures_expiry}
          className="form-select form-select-sm"
        >
          {options &&
            options.map((option) => (
              <option value={option.value}>{option.caption}</option>
            ))}
        </select>
      </div>
    </div>
  );
};
export default ImpliedFuturesExpiry;
