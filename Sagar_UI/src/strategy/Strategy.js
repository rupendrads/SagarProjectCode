import { useState, useRef, useEffect } from "react";
import { Modal } from "bootstrap";
import "./Strategy.css";
import Leg from "./Leg/Leg";
import Sidebar from "./sidebar/Sidebar";
import { useParams } from "react-router-dom";
import { OverallStrategy } from "./overallstrategy/OverallStrategy";
import { defaultOverallStrategy } from "./overallstrategy/defaultOverallStrategy";
import { defaultLeg } from "./Leg/defaultLeg";
import configData from "../config.json";

const Strategy = () => {
  const refModal = useRef(null);
  const refModalInput = useRef();
  const refInfoModal = useRef(null);
  // const [showInfoModal, setShowInfoModal] = useState(false);
  const { id } = useParams();

  const [overallStrategy, setOverallStrategy] = useState({
    ...defaultOverallStrategy,
  });

  const [legs, setLegs] = useState([{ ...defaultLeg }]);

  const [refreshStrategiesList, setRefreshStrategiesList] = useState(false);

  const [isExistingStrategy, setIsExistingStrategy] = useState(false);
  const [responseStatus, setResponseStatus] = useState();

  useEffect(() => {
    if (refModal.current) {
      refModal.myModal = new Modal(refModal.current, { backdrop: "static" });
    }
  }, [refModal]);

  useEffect(() => {
    if (refInfoModal.current) {
      refInfoModal.infoModal = new Modal(refInfoModal.current, {
        backdrop: "static",
      });
    }
  }, [refInfoModal]);

  useEffect(() => {
    console.log("id: ", { id });
    if (id !== undefined) {
      setIsExistingStrategy(true);
      console.log("API_URL", configData.API_URL);
      try {
        fetch(`${configData.API_URL}/strategies/${id}`)
          .then((res) => {
            console.log(res);
            setResponseStatus(res.status);
            if (res.ok === true) return res.json();
            else throw new Error("Status code error :" + res.status);
          })
          .then((data) => {
            console.log("existing data - ", data);
            setOverallStrategy({
              id: data.id,
              name: data.name,
              underlying: data.underlying,
              strategy_type: data.strategy_type,
              implied_futures_expiry: data.implied_futures_expiry,
              entry_time: data.entry_time,
              last_entry_time: data.last_entry_time,
              exit_time: data.exit_time,
              square_off: data.square_off,
              overall_sl: data.overall_sl,
              overall_target: data.overall_target,
              trailing_options: data.trailing_options,
              profit_reaches: data.profit_reaches,
              lock_profit: data.lock_profit,
              increase_in_profit: data.increase_in_profit,
              trail_profit: data.trail_profit,
            });

            console.log("existing legs -", data.legs);
            setLegs([...data.legs]);
          })
          .catch((error) =>
            console.error("Error receiving strategies:", error)
          );
      } catch (error) {
        console.error("Error receiving strategies:", error);
      }
    } else {
      setIsExistingStrategy(false);
      setOverallStrategy({
        ...defaultOverallStrategy,
      });
      setLegs([{ ...defaultLeg }]);
    }
  }, [id]);

  const getFormData = () => {
    const strategy = {
      id:
        isExistingStrategy == false
          ? (Math.random() + 1).toString()
          : overallStrategy.id,
      name: overallStrategy.name,
      underlying: overallStrategy.underlying,
      strategy_type: overallStrategy.strategy_type,
      implied_futures_expiry: overallStrategy.implied_futures_expiry,
      entry_time: overallStrategy.entry_time,
      last_entry_time: overallStrategy.last_entry_time,
      exit_time: overallStrategy.exit_time,
      square_off: overallStrategy.square_off,
      overall_sl: overallStrategy.overall_sl,
      overall_target: overallStrategy.overall_target,
      trailing_options: overallStrategy.trailing_options,
      profit_reaches: overallStrategy.profit_reaches,
      lock_profit: overallStrategy.lock_profit,
      increase_in_profit: overallStrategy.increase_in_profit,
      trail_profit: overallStrategy.trail_profit,
      legs: [...legs],
    };
    return strategy;
  };

  const onChangeOverallStrategy = (fieldName, fieldValue) => {
    setOverallStrategy((prev) => {
      prev[fieldName] = fieldValue;
      return { ...prev };
    });
  };

  const onChangeLegs = (id, fieldName, fieldValue) => {
    console.log("id", id);
    console.log("fieldName", fieldName);
    console.log("fieldValue", fieldValue);
    console.log(legs);
    setLegs((prev) => {
      const legIndex = prev.findIndex((item) => item.id == id);
      console.log("legIndex", legIndex);
      if (legIndex > -1) {
        prev[legIndex][fieldName] = fieldValue;
      }
      console.log(prev);
      return [...prev];
    });
  };

  const onStrategyNameChanged = (e) => {
    onChangeOverallStrategy("name", e.target.value);
  };

  const addLeg = (e) => {
    console.log(legs);
    const newDefaultLeg = { ...defaultLeg };
    newDefaultLeg.id = (Math.random() + 1).toString();
    setLegs((prevLegs) => [...prevLegs, { ...newDefaultLeg }]);
  };

  const removeLeg = (id) => {
    console.log("removing leg");
    console.log("id-", id);
    console.log("legs-", legs);
    setLegs((prevLegs) => {
      const newLegs = prevLegs.filter((leg) => {
        return leg.id != id;
      });
      return [...newLegs];
    });
  };

  const saveStrategy = async () => {
    console.log("saving strategy");
    const strategy = getFormData();
    console.log("strategy data: -");
    console.log(strategy);
    console.log("isExistingStrategy", isExistingStrategy);
    if (isExistingStrategy === true) {
      try {
        const response = await fetch(`${configData.API_URL}/strategies/${id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(strategy),
        });
        const data = await response.json();
        console.log("Save response", data);
      } catch (error) {
        console.error("Error updating strategy:", error);
      } finally {
        if (refModal.myModal) {
          refModal.myModal.hide();
        }
        showInfoModal();
        setRefreshStrategiesList(!refreshStrategiesList);
      }
    } else {
      try {
        const response = await fetch(`${configData.API_URL}/strategies`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(strategy),
        });
        const data = await response.json();
        console.log("Save response", data);
      } catch (error) {
        console.error("Error adding strategy:", error);
      } finally {
        if (refModal.myModal) {
          refModal.myModal.hide();
        }
        showInfoModal();
        setRefreshStrategiesList(!refreshStrategiesList);
      }
    }
  };

  const closeModal = () => {
    if (refModal.myModal) {
      refModal.myModal.hide();
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
    }
  };

  return (
    <>
      <div className="sidebar">
        <Sidebar refresh={refreshStrategiesList} />
      </div>
      {(isExistingStrategy === true && responseStatus === 404) === false && (
        <div className="content">
          <div className="box overall-strategy-box">
            <OverallStrategy
              overallStrategy={overallStrategy}
              onChangeOverallStrategy={onChangeOverallStrategy}
            />
          </div>
          <div className="box leg-builder-box">
            <div className="cell">
              <h6 className="box-title">Leg Builder</h6>
              <hr />
            </div>
            {
              <>
                {legs.map((leg, index) => {
                  return (
                    <Leg
                      key={leg.id}
                      removeLeg={removeLeg}
                      leg={leg}
                      onChangeLegs={onChangeLegs}
                    />
                  );
                })}
              </>
            }

            <div className="cell save-button-row">
              <button className="btn theme_button" onClick={addLeg}>
                Add Leg
              </button>
              <button
                className="btn theme_button"
                onClick={() => {
                  if (isExistingStrategy) {
                    saveStrategy();
                  } else {
                    if (refModal.myModal) {
                      refModal.myModal.show();
                      refModalInput.current.focus();
                    }
                  }
                }}
              >
                Save Strategy
              </button>
            </div>
          </div>

          <div className="modal" tabIndex={-1} role="dialog" ref={refModal}>
            <div className="modal-dialog modal-dialog-centered" role="document">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title dialog-header">
                    Save New Strategy
                  </h5>
                  <button
                    type="button"
                    class="btn-close"
                    data-bs-dismiss="modal"
                    aria-label="Close"
                  ></button>
                </div>
                <div className="modal-body">
                  <div className="form-group">
                    <label htmlFor="strategyName" className="field-label">
                      Strategy Name
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="strategyName"
                      name="strategyName"
                      value={overallStrategy.name}
                      onChange={onStrategyNameChanged}
                      ref={refModalInput}
                    ></input>
                  </div>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn theme_button"
                    onClick={saveStrategy}
                    disabled={overallStrategy.name.trim().length === 0}
                  >
                    Save Strategy
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={closeModal}
                  >
                    Close
                  </button>
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
                      Strategy Saved Successfully
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
        </div>
      )}
      {(isExistingStrategy === true && responseStatus === 404) === true && (
        <div className="content">
          <div className="box">
            <h3>Strategy Not Found</h3>
          </div>
        </div>
      )}
    </>
  );
};

export default Strategy;
