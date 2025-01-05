export const OptionButtonsWithId = (props) => {
  const { options, selectedValue, callbackFunction } = props;

  return (
    <>
      {options &&
        options.map((option) => {
          const { inputName, inputId, inputLabel, fieldName, fieldValue } =
            option;
          return (
            <>
              <input
                type="radio"
                className="btn-check"
                style={{ padding: "6px" }}
                name={inputName}
                id={inputId}
                autocomplete="off"
                checked={fieldValue == selectedValue}
                value={fieldValue}
                onChange={() => callbackFunction(fieldName, fieldValue)}
              />
              <label
                className="btn btn-outline-success rounded-0"
                for={inputId}
              >
                {inputLabel}
              </label>
            </>
          );
        })}
    </>
  );
};
