import "./Steps.css";

const Steps = (props) => {
  const { step, isNewUser, stepItems, changeStep } = props;
  console.log(props);

  return (
    <>
      <div>
        <h6 className="box-title">Steps</h6>
        <hr />
      </div>
      <ul class="list-group">
        {stepItems &&
          stepItems.map((item, index) => {
            return (
              <li class="list-group-item" className="step-item">
                {isNewUser === true ? (
                  <div className="step">
                    <div className="step-number">
                      <label className="field-label">{item.step}</label>
                    </div>
                    <div className="step-name">
                      <div>
                        <label className="field-label">{item.name}</label>
                      </div>
                      <div>
                        {step > index + 1 ? (
                          <i
                            class="bi bi-check-circle h6"
                            style={{ color: "green" }}
                          ></i>
                        ) : (
                          <i
                            class="bi bi-dash-circle h6"
                            style={{ color: "gray" }}
                          ></i>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div
                    className="step step-edit"
                    onClick={() => changeStep(item.step)}
                  >
                    <div className="step-number">
                      <label className="field-label">{item.step}</label>
                    </div>
                    <div className="step-name">
                      <div>
                        <label className="field-label">{item.name}</label>
                      </div>
                      <div>
                        {item.completed === true ? (
                          <i
                            class="bi bi-check-circle h6"
                            style={{ color: "green" }}
                          ></i>
                        ) : (
                          <i
                            class="bi bi-dash-circle h6"
                            style={{ color: "gray" }}
                          ></i>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </li>
            );
          })}
      </ul>
    </>
  );
};

export default Steps;
