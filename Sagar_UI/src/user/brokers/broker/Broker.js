import { useForm } from "react-hook-form";
import configData from "../../../config.json";
import "./Broker.css";
import { useEffect } from "react";

const Broker = (props) => {
  const { userId, broker, userBroker, close } = props;
  console.log(props);
  const {
    register,
    watch,
    reset,
    handleSubmit,
    formState: { data, errors },
  } = useForm();

  useEffect(() => {
    console.log("userBroker", userBroker);
    console.log(userBroker === undefined);
    if (userBroker === undefined) {
      console.log("resetting");
      reset({
        user_id: userId,
        broker_id: broker?.id,
        api_key: "",
        api_secret: "",
        market_api_key: "",
        market_api_secret: "",
      });
    } else {
      console.log("filling");
      reset(userBroker);
    }
  }, [props]);

  const saveBroker = (data) => {
    console.log({ user_id: userId, broker_id: broker.id, ...data });
    const userBrokerData = { user_id: userId, broker_id: broker.id, ...data };
    console.log("userBrokerData", userBrokerData);

    if (configData.JSON_DB === false) {
      if (userBrokerData.hasOwnProperty("id")) {
        try {
          fetch(`${configData.API_URL}/editUserBroker/${userBrokerData.id}`, {
            method: "POST",
            body: JSON.stringify(userBrokerData),
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("user's edit broker response - ", data);
            });
        } catch (error) {
          console.error("Error updating user's broker:", error);
        } finally {
        }
      } else {
        try {
          fetch(`${configData.API_URL}/addUserBroker`, {
            method: "POST",
            body: JSON.stringify(userBrokerData),
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("user's add broker response - ", data);
            });
        } catch (error) {
          console.error("Error adding user's broker:", error);
        } finally {
        }
      }
    } else {
      if (userBrokerData.hasOwnProperty("id")) {
        try {
          fetch(`${configData.API_URL}/userBrokers/${userBrokerData.id}`, {
            method: "PUT",
            body: JSON.stringify(userBrokerData),
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("user's broker response - ", data);
            });
        } catch (error) {
          console.error("Error saving user's broker:", error);
        } finally {
        }
      } else {
        try {
          fetch(`${configData.API_URL}/userBrokers`, {
            method: "POST",
            body: JSON.stringify(userBrokerData),
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => res.json())
            .then((data) => {
              console.log("user's broker response - ", data);
            });
        } catch (error) {
          console.error("Error saving user's broker:", error);
        } finally {
        }
      }
    }

    close();
  };

  return (
    <div className="broker-container">
      <div className="box card" style={{ width: "100%" }}>
        <div>
          <h6 className="box-title">{broker?.name} Setup</h6>
          <hr />
        </div>
        <form onSubmit={handleSubmit(saveBroker)}>
          <div className="broker-input">
            <div className="label">
              <label className="field-label">Interactive API Key</label>
            </div>
            <div className="broker-input-cell">
              <div className="input-group input-group-sm">
                <input
                  type="text"
                  className="form-control"
                  {...register("api_key", { required: true })}
                ></input>
              </div>

              <div className="input-error">
                {errors.api_key && <span>Required</span>}
              </div>
            </div>
          </div>
          <div className="broker-input">
            <div className="label">
              <label className="field-label">Interactive API Secret</label>
            </div>
            <div className="broker-input-cell">
              <div className="input-group input-group-sm">
                <input
                  type="text"
                  className="form-control"
                  {...register("api_secret", { required: true })}
                ></input>
              </div>

              <div className="input-error">
                {errors.api_secret && <span>Required</span>}
              </div>
            </div>
          </div>
          <div className="broker-input">
            <div className="label">
              <label className="field-label">Market API Key</label>
            </div>
            <div className="broker-input-cell">
              <div className="input-group input-group-sm">
                <input
                  type="text"
                  className="form-control"
                  {...register("market_api_key", { required: true })}
                ></input>
              </div>

              <div className="input-error">
                {errors.market_api_key && <span>Required</span>}
              </div>
            </div>
          </div>
          <div className="broker-input">
            <div className="label">
              <label className="field-label">Market API Secret</label>
            </div>
            <div className="broker-input-cell">
              <div className="input-group input-group-sm">
                <input
                  type="text"
                  className="form-control"
                  {...register("market_api_secret", { required: true })}
                ></input>
              </div>

              <div className="input-error">
                {errors.market_api_secret && <span>Required</span>}
              </div>
            </div>
          </div>
          <div className="broker-button-row">
            <button className="btn theme_button" type="submit">
              Update
            </button>
            <button
              type="button"
              className="btn btn-light ok-button"
              onClick={close}
            >
              Close
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Broker;
