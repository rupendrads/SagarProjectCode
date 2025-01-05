export const SelectDDWithKeyIndex = (props) => {
  const { fieldName, selectedValue, options, callbackFunction } = props;
  return (
    <select
      name={fieldName}
      value={selectedValue}
      className="form-select form-select-sm"
      onChange={(e) => callbackFunction(fieldName, e.target.value)}
    >
      {options &&
        options.map((key, index) => {
          return (
            <option key={index} value={key}>
              {key}
            </option>
          );
        })}
    </select>
  );
};
