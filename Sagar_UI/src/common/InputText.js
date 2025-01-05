export const InputText = (props) => {
  const { name, value, callbackFunction } = props;
  return (
    <input
      type="text"
      className="form-control"
      id={name}
      name={name}
      value={value}
      onChange={(e) => callbackFunction(name, e.target.value)}
    ></input>
  );
};
