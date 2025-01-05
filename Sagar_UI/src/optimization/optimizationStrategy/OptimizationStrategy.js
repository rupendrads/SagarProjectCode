import { useEffect, useRef, useState } from "react";
import { OverallStrategy } from "../../strategy/overallstrategy/OverallStrategy";
import Leg from "../../strategy/Leg/Leg";
import generateKeyResponseData from "./generateKeyResponse.json";
import runOptimizationResponseData from "./runOptimizationResponse.json";
import retryOptimizationResponseData from "./retryOptimizationResponse.json";
import getTradebookResponseData from "./getTradebookResponse.json";
import configData from "../../config.json";
import "./OptimizationStrategy.css";
import OptimizationReport from "../optimizationReport/OptimizationReport";
import OptimizationVariables from "../optimizationVariables/OptimizationVariables";
import { positiveNumberOnly } from "../../common/InputValidation";
import TradeBookReport from "../optimizationReport/tradeBook/TradeBookReport";
import { Modal } from "bootstrap";

const OptimizationStrategy = (props) => {
  const { strategy } = props;
  const refTradeBookModel = useRef(null);
  const [overallStrategy, setOverallStrategy] = useState(undefined);
  const [optimizationParameters, setOptimizationParameters] =
    useState(undefined);
  const [legs, setLegs] = useState([]);
  const [extraInfo, setExtraInfo] = useState({
    fromdate: new Date(0),
    todate: new Date(0),
    index: "nifty",
    brokerage: "",
    slippage: "",
  });
  const [reportData, setReportData] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showHideStrategy, setShowHideStrategy] = useState(true);
  const [combinationCount, setCombinationCount] = useState(0);
  const [sequenceNumber, setSequenceNumber] = useState(0);
  const [progressValue, setProgressValue] = useState(0);
  const [incrementor, setIncrementor] = useState(0);
  const [tradeBookReportData, setTradeBookReportData] = useState(undefined);
  const [optimizationKey, setOptimizationKey] = useState(undefined);

  const fillPageWithData = (optimizationData) => {
    setOverallStrategy({
      id: optimizationData.full_json.strategy_parameter.id,
      name: optimizationData.full_json.strategy_parameter.name,
      underlying: optimizationData.full_json.strategy_parameter.underlying,
      strategy_type:
        optimizationData.full_json.strategy_parameter.strategy_type,
      implied_futures_expiry:
        optimizationData.full_json.strategy_parameter.implied_futures_expiry,
      entry_time: optimizationData.full_json.strategy_parameter.entry_time,
      last_entry_time:
        optimizationData.full_json.strategy_parameter.last_entry_time,
      exit_time: optimizationData.full_json.strategy_parameter.exit_time,
      square_off: optimizationData.full_json.strategy_parameter.square_off,
      overall_sl: optimizationData.full_json.strategy_parameter.overall_sl,
      overall_target:
        optimizationData.full_json.strategy_parameter.overall_target,
      trailing_options:
        optimizationData.full_json.strategy_parameter.trailing_options,
      profit_reaches:
        optimizationData.full_json.strategy_parameter.profit_reaches,
      lock_profit: optimizationData.full_json.strategy_parameter.lock_profit,
      increase_in_profit:
        optimizationData.full_json.strategy_parameter.increase_in_profit,
      trail_profit: optimizationData.full_json.strategy_parameter.trail_profit,
    });
    setLegs([...optimizationData.full_json.strategy_parameter.legs]);
    setOptimizationParameters({
      overallStrategy:
        optimizationData.full_json.optimization_parameter.overallStrategy,
      legs: optimizationData.full_json.optimization_parameter.legs,
    });
    setExtraInfo({
      fromdate: optimizationData.full_json.optimization_parameter.fromdate,
      todate: optimizationData.full_json.optimization_parameter.todate,
      index: optimizationData.full_json.optimization_parameter.index,
      brokerage: optimizationData.full_json.optimization_parameter.brokerage,
      slippage: optimizationData.full_json.optimization_parameter.slippage,
    });
  };

  const fillReportWithData = (data) => {
    setReportData([...data.completed_combinations]);
  };

  const fillProgressBar = (data) => {
    console.log(
      "fill progress - sequence start",
      data.pending_combinations.sequence_start
    );
    console.log(
      "fill progress - sequence completed",
      data.pending_combinations.sequence_start - 1
    );
    const incrementor = 100 / data.pending_combinations.total_count;
    setIncrementor(incrementor);
    console.log("fill progress - incrementor", incrementor);
    setProgressValue(
      incrementor * (data.pending_combinations.sequence_start - 1)
    );
  };

  useEffect(() => {
    console.log("processing optimization - check for exising key");
    const optimizationKey = localStorage.getItem("optimizationKey");
    console.log("processing optimization - key", optimizationKey);
    if (optimizationKey && optimizationKey !== null) {
      if (
        window.confirm("PREVIOUS Optimization is pending. You want to run?")
      ) {
        const retryOptimizationRequest = {
          optimization_key: optimizationKey,
        };
        console.log(
          "processing optimization - retryOptimization request",
          retryOptimizationRequest
        );
        setIsProcessing(true);
        if (configData.JSON_DB === false) {
          try {
            fetch(`${configData.OPTIMIZATION_API_URL}/retryOptimization`, {
              method: "POST",
              body: JSON.stringify(retryOptimizationRequest),
              headers: { "Content-type": "application/json; charset=UTF-8" },
            })
              .then((res) => res.json())
              .then((data) => {
                console.log(
                  "processing optimization - retryOptimization response",
                  data
                );
                setOptimizationKey(optimizationKey);
                fillPageWithData(data);
                fillReportWithData(data);
                fillProgressBar(data);
                setCombinationCount(data.pending_combinations.total_count);
                setSequenceNumber(data.pending_combinations.sequence_start);
              });
          } catch (error) {
            console.error(
              "processing optimization - Error receiving retry optimization response:",
              error
            );
            setIsProcessing(false);
          }
        } else {
          try {
            console.log(
              console.log(
                "processing optimization - retryOptimization response",
                retryOptimizationResponseData
              )
            );
            setOptimizationKey(optimizationKey);
            fillPageWithData(retryOptimizationResponseData);
            fillReportWithData(retryOptimizationResponseData);
            fillProgressBar(retryOptimizationResponseData);
            setCombinationCount(
              retryOptimizationResponseData.pending_combinations.total_count
            );
            setSequenceNumber(
              retryOptimizationResponseData.pending_combinations.sequence_start
            );
          } catch (error) {
            console.error(
              "processing optimization - Error receiving retry optimization response:",
              error
            );
            setIsProcessing(false);
          }
        }
      }
    }
  }, []);

  useEffect(() => {
    if (strategy !== undefined) {
      console.log("strategy changed");
      localStorage.removeItem("optimizationKey");
      setReportData(undefined);
      setTradeBookReportData(undefined);
      setProgressValue(0);
      setIsProcessing(false);

      setOverallStrategy({
        id: strategy.id,
        name: strategy.name,
        underlying: strategy.underlying,
        strategy_type: strategy.strategy_type,
        implied_futures_expiry: strategy.implied_futures_expiry,
        entry_time: strategy.entry_time,
        last_entry_time: strategy.last_entry_time,
        exit_time: strategy.exit_time,
        square_off: strategy.square_off,
        overall_sl: strategy.overall_sl,
        overall_target: strategy.overall_target,
        trailing_options: strategy.trailing_options,
        profit_reaches: strategy.profit_reaches,
        lock_profit: strategy.lock_profit,
        increase_in_profit: strategy.increase_in_profit,
        trail_profit: strategy.trail_profit,
      });
      setLegs([...strategy.legs]);

      setOptimizationParameters(() => {
        const overallStrategy = {
          id: strategy.id,
          name: strategy.name,
          underlying: strategy.underlying,
          strategy_type: strategy.strategy_type,
          implied_futures_expiry: strategy.implied_futures_expiry,
          entry_time: {
            min: "",
            max: "",
            interval: "",
          },
          exit_time: {
            min: "",
            max: "",
            interval: "",
          },
          last_entry_time: {
            min: "",
            max: "",
            interval: "",
          },
          square_off: strategy.square_off,
          overall_sl: {
            min: "",
            max: "",
            interval: "0",
          },
          overall_target: {
            min: "",
            max: "",
            interval: "0",
          },
          trailing_options: strategy.trailing_options,
          profit_reaches: {
            min: "",
            max: "",
            interval: "0",
          },
          lock_profit: {
            min: "",
            max: "",
            interval: "0",
          },
          increase_in_profit: {
            min: "",
            max: "",
            interval: "0",
          },
          trail_profit: {
            min: "",
            max: "",
            interval: "0",
          },
        };
        let legs = [];
        strategy.legs.map((leg) => {
          //console.log(leg);
          const legItem = {
            id: leg.id,
            lots: leg.lots,
            position: leg.position,
            option_type: leg.option_type,
            expiry: leg.expiry,
            no_of_reentry: {
              min: leg.no_of_reentry,
              max: "",
              interval: "",
            },
            strike_selection_criteria: leg.strike_selection_criteria,
            closest_premium: {
              min: leg.closest_premium,
              max: "",
              interval: "",
            },
            strike_type: {
              min: "-20",
              max: "20",
              interval: "1",
            },
            straddle_width_value: {
              min: leg.straddle_width_value,
              max: "",
              interval: "",
            },
            straddle_width_sign: leg.straddle_width_sign,
            percent_of_atm_strike_value: {
              min: leg.percent_of_atm_strike_value,
              max: "",
              interval: "",
            },
            percent_of_atm_strike_sign: leg.percent_of_atm_strike_sign,
            atm_straddle_premium: {
              min: leg.atm_straddle_premium,
              max: "100",
              interval: "",
            },
            strike_selection_criteria_stop_loss: {
              min: leg.strike_selection_criteria_stop_loss,
              max: "",
              interval: "",
            },
            strike_selection_criteria_stop_loss_sign:
              leg.strike_selection_criteria_stop_loss_sign,
            strike_selection_criteria_trailing_options:
              leg.strike_selection_criteria_trailing_options,
            strike_selection_criteria_profit_reaches: {
              min: leg.strike_selection_criteria_profit_reaches,
              max: "",
              interval: "",
            },
            strike_selection_criteria_lock_profit: {
              min: leg.strike_selection_criteria_lock_profit,
              max: "",
              interval: "",
            },
            strike_selection_criteria_lock_profit_sign:
              leg.strike_selection_criteria_lock_profit_sign,
            strike_selection_criteria_increase_in_profit: {
              min: leg.strike_selection_criteria_increase_in_profit,
              max: "",
              interval: "",
            },
            strike_selection_criteria_trail_profit: {
              min: leg.strike_selection_criteria_trail_profit,
              max: "",
              interval: "",
            },
            strike_selection_criteria_trail_profit_sign:
              leg.strike_selection_criteria_trail_profit_sign,
            roll_strike: {
              min: leg.roll_strike,
              max: "",
              interval: "",
            },
            roll_strike_strike_type: {
              min: "",
              max: "",
              interval: "",
            },
            roll_strike_stop_loss: {
              min: leg.roll_strike_stop_loss,
              max: "",
              interval: "",
            },
            roll_strike_stop_loss_sign: leg.roll_strike_stop_loss_sign,
            roll_strike_trailing_options: leg.roll_strike_trailing_options,
            roll_strike_profit_reaches: {
              min: leg.roll_strike_profit_reaches,
              max: "",
              interval: "",
            },
            roll_strike_lock_profit: {
              min: leg.roll_strike_lock_profit,
              max: "",
              interval: "",
            },
            roll_strike_lock_profit_sign: leg.roll_strike_lock_profit_sign,
            roll_strike_increase_in_profit: {
              min: leg.roll_strike_increase_in_profit,
              max: "",
              interval: "",
            },
            roll_strike_trail_profit: {
              min: leg.roll_strike_trail_profit,
              max: "",
              interval: "",
            },
            roll_strike_trail_profit_sign: leg.roll_strike_trail_profit_sign,
            simple_momentum_range_breakout: leg.simple_momentum_range_breakout,
            simple_momentum: {
              min: leg.simple_momentum,
              max: "",
              interval: "",
            },
            simple_momentum_sign: leg.simple_momentum_sign,
            simple_momentum_direction: leg.simple_momentum_direction,
            range_breakout: {
              min: leg.range_breakout,
              max: "",
              interval: "",
            },
          };
          legs.push({ ...legItem });
        });
        return { overallStrategy: overallStrategy, legs: legs };
      });

      setExtraInfo({
        fromdate: new Date(0),
        todate: new Date(0),
        index: "nifty",
        brokerage: "",
        slippage: "",
      });
    }
  }, [strategy]);

  useEffect(() => {
    if (combinationCount > 0 && sequenceNumber > 0) {
      console.log(
        `processing optimization run ${sequenceNumber} of ${combinationCount}`
      );
      //const optimizationKey = localStorage.getItem("optimizationKey");
      if (configData.JSON_DB === false) {
        if (optimizationKey && optimizationKey !== null) {
          const runOptimizationRequest = {
            optimization_key: optimizationKey,
            sequence_id: sequenceNumber,
          };
          console.log(
            "processing optimization run request - ",
            runOptimizationRequest
          );
          try {
            fetch(`${configData.OPTIMIZATION_RUN_API_URL}/runOptimization`, {
              method: "POST",
              body: JSON.stringify(runOptimizationRequest),
              headers: { "Content-type": "application/json; charset=UTF-8" },
            })
              .then((res) => res.json())
              .then((data) => {
                console.log("processing optimization run response - ", data);
                if (data.status === "success") {
                  console.log("processing optimization run response - ", {
                    ...data,
                  });
                  setReportData((prevState) => {
                    return [...prevState, data];
                  });
                  setProgressValue((prevValue) => {
                    return prevValue + incrementor;
                  });
                  const newSequenceNumber = sequenceNumber + 1;
                  if (newSequenceNumber > combinationCount) {
                    console.log("processing optimization - removing key");
                    localStorage.removeItem("optimizationKey");
                    setSequenceNumber(0);
                    setIsProcessing(false);
                  } else {
                    setSequenceNumber(newSequenceNumber);
                  }
                } else {
                  console.error(
                    `processing optimization failed for sequence number ${data.sequence_id}`
                  );
                }
              });
          } catch (error) {
            console.error(
              "processing optimization - Error receiving run optimization response:",
              error
            );
          } finally {
          }
        }
      } else {
        if (optimizationKey !== null) {
          const runOptimizationRequest = {
            optimization_key: optimizationKey,
            sequence_id: sequenceNumber,
          };
          console.log(
            "processing optimization run request - ",
            runOptimizationRequest
          );
          setTimeout(() => {
            console.log("processing optimization run response - ", {
              ...runOptimizationResponseData,
            });
            setReportData((prevState) => {
              return [...prevState, runOptimizationResponseData];
            });
            setProgressValue((prevValue) => {
              return prevValue + incrementor;
            });
            const newSequenceNumber = sequenceNumber + 1;
            if (newSequenceNumber > combinationCount) {
              console.log("processing optimization - removing key");
              localStorage.removeItem("optimizationKey");
              setSequenceNumber(0);
              setIsProcessing(false);
            } else {
              setSequenceNumber(newSequenceNumber);
            }
          }, 5000);
        }
      }
    }
  }, [combinationCount, sequenceNumber]);

  useEffect(() => {
    if (refTradeBookModel.current) {
      refTradeBookModel.tradeBookModal = new Modal(refTradeBookModel.current, {
        backdrop: "static",
      });
    }
  }, [refTradeBookModel]);

  const showTradeBookModel = () => {
    console.log("showing tradebook modal");

    if (refTradeBookModel.tradeBookModal) {
      refTradeBookModel.tradeBookModal.show();
    }
  };

  const hideTradeBookModel = () => {
    if (refTradeBookModel.tradeBookModal) {
      refTradeBookModel.tradeBookModal.hide();
    }
  };

  const getOptimzationKey = () => {
    const dt = new Date();
    console.log("optimization key date", dt);
    const year = dt.getFullYear().toString();
    console.log("optimization key year", year);
    const month = (dt.getMonth() + 1).toString();
    console.log("optimization key month", month);
    const day = dt.getDate().toString();
    console.log("optimization key day", day);
    const hours = dt.getHours().toString();
    console.log("optimization key hours", hours);
    const seconds = dt.getSeconds().toString();
    console.log("optimization key seconds", seconds);
    const key =
      year +
      (month.length === 1 ? "0" + month : month) +
      (day.length === 1 ? "0" + day : day) +
      hours +
      seconds +
      "_" +
      strategy.name;
    console.log("optimization key", key);
    return key;
  };

  const optimizeStrategy = () => {
    const optimizationParametersWithExtraInfo = {
      ...optimizationParameters,
      ...extraInfo,
    };
    const optimizationKey = getOptimzationKey();
    const optimizationRequest = {
      optimization_key: optimizationKey,
      optimization_parameter: { ...optimizationParametersWithExtraInfo },
      strategy_parameter: { ...strategy },
    };

    console.log(
      "processing optimization generateKey request - ",
      optimizationRequest
    );

    setProgressValue(0);
    setReportData([]);
    setIsProcessing(true);
    if (configData.JSON_DB === false) {
      // code only for optimization api start
      try {
        fetch(`${configData.OPTIMIZATION_API_URL}/generateKey`, {
          method: "POST",
          body: JSON.stringify(optimizationRequest),
          headers: { "Content-type": "application/json; charset=UTF-8" },
        })
          .then((res) => res.json())
          .then((data) => {
            localStorage.setItem("optimizationKey", optimizationKey);
            setOptimizationKey(optimizationKey);

            const optimizationCount = data.total_number_of_combinations;

            console.log(
              "processing optimization generateKey response - ",
              data
            );

            const incrementor = 100 / optimizationCount;
            setIncrementor(incrementor);

            setCombinationCount(optimizationCount);
            setSequenceNumber(1);
          });
      } catch (error) {
        console.error(
          "processing optimization -Error receiving generateKey response:",
          error
        );
      } finally {
      }
      // code only for backtest api end
    } else {
      // code only for json data start
      setTimeout(() => {
        localStorage.setItem("optimizationKey", optimizationKey);
        setOptimizationKey(optimizationKey);

        const optimizationCount =
          generateKeyResponseData.total_number_of_combinations;

        console.log(
          "processing optimization generateKey response - ",
          generateKeyResponseData
        );

        const incrementor = 100 / optimizationCount;
        setIncrementor(incrementor);

        setCombinationCount(optimizationCount);
        setSequenceNumber(1);
      }, 3000);

      // code only for json data end
    }
  };

  const onIndexChanged = (e) => {
    //console.log(e.target.value);
    setExtraInfo({ ...extraInfo, index: e.target.value });
  };

  const fromDateChanged = (e) => {
    console.log("from date", e.target.value);
    setExtraInfo({ ...extraInfo, fromdate: e.target.value });
  };

  const toDateChanged = (e) => {
    console.log("to date", e.target.value);
    setExtraInfo({ ...extraInfo, todate: e.target.value });
  };

  const onbrokerageChanged = (e) => {
    setExtraInfo({ ...extraInfo, brokerage: e.target.value });
  };

  const onSlippageChanged = (e) => {
    setExtraInfo({ ...extraInfo, slippage: e.target.value });
  };

  const onChangeOptimizationParameters = (fieldName, fieldValue) => {
    console.log("fieldName", fieldName);
    console.log("fieldValue", fieldValue);
    setOptimizationParameters((prev) => {
      console.log(prev);
      if (fieldName.includes(".")) {
        const first = fieldName.split(".")[0];
        const second = fieldName.split(".")[1];
        prev.overallStrategy[first][second] = fieldValue;
      } else {
        prev.overallStrategy[fieldName] = fieldValue;
      }
      return { ...prev };
    });
  };

  const onChangeLegs = (id, fieldName, fieldValue) => {
    console.log("id", id);
    console.log("fieldName", fieldName);
    console.log("fieldValue", fieldValue);
    console.log(legs);
    setOptimizationParameters((prev) => {
      console.log(prev);
      const legIndex = prev.legs.findIndex((item) => item.id == id);
      console.log("legIndex", legIndex);
      if (legIndex > -1) {
        if (fieldName.includes(".")) {
          const first = fieldName.split(".")[0];
          const second = fieldName.split(".")[1];
          prev.legs[legIndex][first][second] = fieldValue;
        } else {
          prev.legs[legIndex][fieldName] = fieldValue;
        }
      }
      console.log(prev);
      return { ...prev };
    });
  };

  const StrategyBoxStyle = {
    maxHeight: showHideStrategy === true ? "8000px" : "0px",
  };

  const toggleStrategy = () => {
    setShowHideStrategy(!showHideStrategy);
  };

  const getTradeBookReport = (sequence_id) => {
    console.log("sequence_id", sequence_id);
    //const optimizationKey = localStorage.getItem("optimizationKey");
    if (optimizationKey) {
      if (configData.JSON_DB === false) {
        const getTradeBookRequest = {
          optimization_key: optimizationKey,
          sequence_id: sequence_id,
        };
        try {
          fetch(`${configData.OPTIMIZATION_API_URL}/gettradebook`, {
            method: "POST",
            body: JSON.stringify(getTradeBookRequest),
            headers: { "Content-type": "application/json; charset=UTF-8" },
          })
            .then((res) => res.json())
            .then((data) => {
              setTradeBookReportData(data);
              //showTradeBookReport(true);
              showTradeBookModel();
            });
        } catch (error) {
          console.error(
            "processing optimization -Error gettradebook response:",
            error
          );
        }
      } else {
        console.log("setting tradebook report data");
        setTradeBookReportData(getTradebookResponseData);

        console.log("show trade book model");
        showTradeBookModel();
      }
    }
  };

  return (
    <div className="optimization-strategy-content">
      {overallStrategy !== undefined && (
        <div className="content optimization-strategy-input">
          <div className="show-hide-button-wrapper" onClick={toggleStrategy}>
            <button
              className={`show-hide-button ${
                showHideStrategy === true
                  ? "show-hide-button-up"
                  : "show-hide-button-down"
              }`}
            >
              <i class="bi bi-caret-down-fill"></i>
            </button>
            <span>
              <label
                className={`field-label ${
                  showHideStrategy === true
                    ? "show-hide-label-animate"
                    : "show-hide-label"
                }`}
              >
                Hide Default Strategy
              </label>
              <label
                className={`field-label ${
                  showHideStrategy === false
                    ? "show-hide-label-animate"
                    : "show-hide-label"
                }`}
              >
                Show Default Strategy
              </label>
            </span>
          </div>
          <div className="optimization-strategy-box" style={StrategyBoxStyle}>
            <div className="box">
              <div className="cell">
                <h6 className="box-title optimization-strategy-box-title">
                  Default Strategy
                </h6>
                <hr className="title-hr" />
              </div>
            </div>
            <div className="box overall-strategy-box" disabled>
              <OverallStrategy overallStrategy={overallStrategy} />
            </div>
            <div className="box leg-builder-box" disabled>
              <div className="cell">
                <h6 className="box-title">Legs</h6>
                <hr />
              </div>
              {
                <>
                  {legs.map((leg, index) => {
                    return <Leg key={leg.id} leg={leg} />;
                  })}
                </>
              }
            </div>
          </div>
          {optimizationParameters !== undefined && (
            <div className="optimization-strategy-box">
              <div className="box">
                <div className="cell">
                  <h6 className="box-title optimization-strategy-box-title">
                    Optimization Parameters
                  </h6>
                  <hr className="title-hr" />
                </div>
              </div>
              <OptimizationVariables
                optimizationParameters={optimizationParameters}
                onChangeOptimizationParameters={onChangeOptimizationParameters}
                onChangeLegs={onChangeLegs}
              />
            </div>
          )}

          <div className="box leg-builder-box">
            <div className="cell optimization-save-button-row">
              <div className="optimization-brokerage-wrapper input-group-sm">
                <label className="field-label optimization-extra-info-label ">
                  Broekrage
                </label>
                <input
                  type="text"
                  id="brokerage"
                  name="brokerage"
                  onKeyDown={positiveNumberOnly}
                  value={extraInfo.brokerage}
                  className="form-control"
                  onChange={onbrokerageChanged}
                />
              </div>
              <div className="optimization-brokerage-wrapper input-group-sm">
                <label className="field-label optimization-extra-info-label ">
                  Slippage
                </label>
                <input
                  type="text"
                  id="slippage"
                  name="slippage"
                  onKeyDown={positiveNumberOnly}
                  value={extraInfo.slippage}
                  className="form-control"
                  onChange={onSlippageChanged}
                />
              </div>
              <div className="optimization-index-wrapper">
                <label className="field-label optimization-extra-info-label">
                  Index
                </label>
                <select
                  id="instrument"
                  name="instrument"
                  value={extraInfo.index}
                  className="form-select form-select-sm"
                  onChange={onIndexChanged}
                >
                  <option value="nifty">Nifty</option>
                  <option value="banknifty">Banknifty</option>
                  <option value="finnifty">Finnifty</option>
                </select>
              </div>
              <div className="optimization-date-input-wrapper-div">
                <div className="optimization-date-input-wrapper">
                  <div className="optimization-extra-info-label-wrapper">
                    <label className="field-label optimization-extra-info-label">
                      From date
                    </label>
                  </div>
                  <div className="input-group input-group-sm">
                    <input
                      type="date"
                      id="from-date"
                      name="from-date"
                      className="form-control"
                      value={extraInfo.fromdate}
                      onChange={fromDateChanged}
                    ></input>
                  </div>
                </div>
                <div className="optimization-date-input-wrapper">
                  <div className="optimization-extra-info-label-wrapper">
                    <label className="field-label optimization-extra-info-label">
                      To date
                    </label>
                  </div>
                  <div className="input-group input-group-sm">
                    <input
                      type="date"
                      id="to-date"
                      name="to-date"
                      className="form-control"
                      value={extraInfo.todate}
                      onChange={toDateChanged}
                    ></input>
                  </div>
                </div>
              </div>
              <div>
                <button
                  id="btn_optimization_strategy"
                  className="btn theme_button"
                  onClick={optimizeStrategy}
                  disabled={isProcessing === true}
                >
                  {isProcessing === true && (
                    <>
                      <span
                        class="spinner-border spinner-border-sm"
                        role="status"
                        aria-hidden="true"
                      ></span>
                      &nbsp;&nbsp;<span>Processing...</span>
                    </>
                  )}
                  {isProcessing === false && <span>Optimize Strategy</span>}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {isProcessing === true && sequenceNumber > 0 && (
        <div className="file-counter">
          <div className="cell">
            <label>
              Optimizing {sequenceNumber} of {combinationCount}
            </label>
          </div>
        </div>
      )}
      {progressValue === 100 && (
        <div className="file-counter">
          <div className="cell">
            <label>
              Optimization Completed {combinationCount} of {combinationCount}
            </label>
          </div>
        </div>
      )}
      {(isProcessing === true || progressValue > 0) && (
        <div className="cell">
          <div class="progress">
            <div
              class="progress-bar bg-success"
              role="progressbar"
              style={{ width: progressValue.toString() + "%" }}
              aria-valuemin="0"
              aria-valuemax="100"
            ></div>
          </div>
        </div>
      )}
      {reportData && reportData.length > 0 && (
        <div className="content">
          <OptimizationReport
            data={reportData}
            dataLength={combinationCount}
            getTradeBookReport={getTradeBookReport}
          />
        </div>
      )}
      <div
        className="modal"
        tabIndex={-1}
        role="dialog"
        ref={refTradeBookModel}
      >
        <div
          className="modal-dialog modal-dialog-centered modal-lg"
          role="document"
        >
          <div className="modal-content">
            <div className="modal-body">
              <div className="form-group info-modal-body">
                <div className="content">
                  {tradeBookReportData && (
                    <TradeBookReport data={tradeBookReportData} />
                  )}
                </div>
              </div>
            </div>
            <div className="modal-footer info-modal-footer">
              <button
                type="button"
                className="btn btn-light ok-button"
                onClick={hideTradeBookModel}
              >
                Ok
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OptimizationStrategy;
