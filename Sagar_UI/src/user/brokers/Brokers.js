import { useEffect, useRef, useState } from "react";
import { Modal } from "bootstrap";
import Broker from "./broker/Broker";
import "./Brokers.css";
import Steps from "../steps/Steps";
import configData from "../../config.json";
import { useNavigate } from "react-router-dom";

const Brokers = (props) => {
  console.log("props", props);
  const { userId, isNewUser, forwardStep, stepItems, changeStep } = props;
  const [brokersList, setBrokersList] = useState([]);
  const [userBrokersList, setUserBrokersList] = useState([]);
  const [selectedBroker, setSelectedBroker] = useState(undefined);
  const [step, setStep] = useState(4);
  const navigate = useNavigate();

  const refBrokerModel = useRef(null);
  const refInfoModal = useRef(null);

  useEffect(() => {
    let urlSegment = "broker";

    if (configData.JSON_DB === false) {
      urlSegment = "getAllBrokers";
    }

    try {
      fetch(`${configData.API_URL}/${urlSegment}`, {
        method: "GET",
        headers: { "Content-type": "application/json; charset=UTF-8" },
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("brokers response - ", data);
          setBrokersList([...data]);
        });
    } catch (error) {
      console.error("Error receiving brokers:", error);
    } finally {
    }
  }, []);

  useEffect(() => {
    if (selectedBroker === undefined) {
      let urlSegment = "userBrokers";

      if (configData.JSON_DB === false) {
        urlSegment = "getAllUserBroker";
      }

      try {
        fetch(`${configData.API_URL}/${urlSegment}`, {
          method: "GET",
          headers: { "Content-type": "application/json; charset=UTF-8" },
        })
          .then((res) => res.json())
          .then((data) => {
            console.log("user brokers response - ", data);
            if (configData.JSON_DB === false) {
              setUserBrokersList(() => {
                const formattedData = [];
                for (var i = 0; i < data.length; i++) {
                  const item = data[i];
                  formattedData.push({
                    id: item.id,
                    user_id: item.user_id,
                    broker_id: item.broker_id,
                    api_key: item.API_Key,
                    api_secret: item.API_Secret,
                    market_api_key: item.market_api_key,
                    market_api_secret: item.market_api_secret,
                  });
                }
                return [...formattedData];
              });
            } else {
              setUserBrokersList([...data]);
            }
          });
      } catch (error) {
        console.error("Error receiving user brokers - ", error);
      } finally {
      }
    }
  }, [selectedBroker]);

  useEffect(() => {
    if (refBrokerModel.current) {
      refBrokerModel.brokerModal = new Modal(refBrokerModel.current, {
        backdrop: "static",
      });
    }
  }, [refBrokerModel]);

  useEffect(() => {
    if (refInfoModal.current) {
      refInfoModal.infoModal = new Modal(refInfoModal.current, {
        backdrop: "static",
      });
    }
  }, [refInfoModal]);

  const displayBrokerModal = () => {
    if (refBrokerModel.brokerModal) {
      refBrokerModel.brokerModal.show();
    }
  };

  const hideBrokerModal = () => {
    if (refBrokerModel.brokerModal) {
      refBrokerModel.brokerModal.hide();
    }
  };

  const showInfoModal = () => {
    console.log("showing info modal");

    if (refInfoModal.infoModal) {
      refInfoModal.infoModal.show();
    }
  };

  const hideInfoModal = () => {
    if (refInfoModal.infoModal) {
      refInfoModal.infoModal.hide();
      navigate("/");
    }
  };

  const setup = (broker) => {
    console.log(broker);
    setSelectedBroker(broker);
    displayBrokerModal();
  };

  const close = () => {
    console.log("closing modal");
    setSelectedBroker(undefined);
    hideBrokerModal();
  };

  const getUserBroker = (id) => {
    console.log("broker id", id);
    console.log("user id", userId);
    console.log("userBrokersList", userBrokersList);
    return userBrokersList.find(
      (ub) => ub.broker_id == id && ub.user_id == userId
    );
  };

  const finishSetup = () => {
    setStep(step + 1);
    setTimeout(() => {
      showInfoModal();
    }, 500);
  };

  return (
    <>
      <div className="registration-sidebar">
        <div className="box card registration-steps-container">
          <Steps
            step={step}
            stepItems={stepItems}
            isNewUser={isNewUser}
            changeStep={changeStep}
          />
        </div>
        <div className="brokers-container">
          <div className="box card" style={{ width: "100%" }}>
            <div>
              <h6 className="box-title">Brokers</h6>
              <hr />
            </div>
            <div className="cell">
              {brokersList &&
                brokersList.map((broker) => {
                  return (
                    <div className="box card broker_setup_card" key={broker.id}>
                      <div className="broker_setup_row">
                        <div className="field-label broker_name">
                          {broker.name}
                        </div>
                        <div>
                          {getUserBroker(broker.id) ? (
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
                        <div className="broker-button-row">
                          <button
                            className="btn btn-light setup-button"
                            onClick={() => setup(broker)}
                          >
                            Setup
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
            <div className="brokers-button-row">
              <button
                className="btn theme_button"
                type="button"
                onClick={finishSetup}
              >
                Finish Setup
              </button>
            </div>
          </div>
          <div
            className="modal"
            tabIndex={-1}
            role="dialog"
            ref={refBrokerModel}
          >
            <div className="modal-dialog modal-dialog-centered" role="document">
              <div className="modal-content">
                <div
                  className="modal-body"
                  style={{
                    display: "flex",
                    justifyContent: "center",
                  }}
                >
                  <Broker
                    broker={selectedBroker}
                    userId={userId}
                    userBroker={
                      selectedBroker
                        ? getUserBroker(selectedBroker.id)
                        : undefined
                    }
                    close={close}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="modal" tabIndex={-1} role="dialog" ref={refInfoModal}>
        <div className="modal-dialog modal-dialog-centered" role="document">
          <div className="modal-content">
            <div className="modal-body">
              <div className="form-group info-modal-body">
                <label className="field-label">
                  {isNewUser ? (
                    <span>User Registration Completed Successfully</span>
                  ) : (
                    <span>User Details Updated Successfully</span>
                  )}
                </label>
              </div>
            </div>
            <div className="modal-footer info-modal-footer">
              <button
                type="button"
                className="btn btn-light ok-button"
                onClick={hideInfoModal}
              >
                Ok
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Brokers;
