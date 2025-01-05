export const SelectDD = (props) => {
  const { fieldName, selectedValue, options, callbackFunction } = props;
  return (
    <select
      name={fieldName}
      value={selectedValue}
      className="form-select form-select-sm"
      onChange={(e) => callbackFunction(fieldName, e.target.value)}
    >
      {options &&
        options.map((option) => (
          <option value={option.value}>{option.caption}</option>
        ))}
    </select>
  );
};
