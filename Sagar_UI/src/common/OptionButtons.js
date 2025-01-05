export const OptionButtons = (props) => {
  const {
    fieldName,
    fieldValuesWithCaptions,
    selectedFieldValue,
    callbackFunction,
  } = props;
  return (
    <>
      {fieldValuesWithCaptions &&
        fieldValuesWithCaptions.map((fieldValueWithCaption) => {
          const fieldValueWithCaptionArray = fieldValueWithCaption.split(",");
          const fieldValue = fieldValueWithCaptionArray[0];
          const fieldValueCaption = fieldValueWithCaptionArray[1];
          return (
            <>
              <input
                type="radio"
                className="btn-check"
                style={{ padding: "6px" }}
                name={fieldName}
                id={`${fieldName}-${fieldValue}`}
                autocomplete="off"
                checked={selectedFieldValue == fieldValue}
                value={fieldValue}
                onChange={() => callbackFunction(fieldName, fieldValue)}
              />
              <label
                className="btn btn-outline-success rounded-0"
                for={`${fieldName}-${fieldValue}`}
              >
                {fieldValueCaption}
              </label>
            </>
          );
        })}
    </>
  );
};
