import { useEffect, useState, useRef } from "react";
import { OverallStrategy } from "../../strategy/overallstrategy/OverallStrategy";
import Leg from "../../strategy/Leg/Leg";
import "./BackTestStrategy.css";
import backTestReportData from "./backtestReport.json";
import { BackTestReport } from "../backtestReport/BackTestReport";
import configData from "../../config.json";
import { saveAs } from "file-saver";
import { Modal } from "bootstrap";

const BackTestStrategy = (props) => {
  console.log("props", props);
  const { strategy, strategyImported } = props;
  const refImportFileModel = useRef(null);
  const refFileInput = useRef(null);
  const [overallStrategy, setOverallStrategy] = useState({});
  const [legs, setLegs] = useState([]);
  const [extraInfo, setExtraInfo] = useState({
    fromdate: undefined,
    todate: undefined,
    index: "nifty",
  });
  const [showBackTestReport, setShowBackTestReport] = useState(false);
  const [reportData, setReportData] = useState(backTestReportData);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (refImportFileModel.current) {
      refImportFileModel.importFileModal = new Modal(
        refImportFileModel.current,
        {
          backdrop: "static",
        }
      );
    }
  }, [refImportFileModel]);

  useEffect(() => {
    console.log("strategy changed");
    if (strategy !== undefined) {
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

      setExtraInfo({
        fromdate: strategy.fromdate ? strategy.fromdate : new Date(0),
        todate: strategy.todate ? strategy.todate : new Date(0),
        index: strategy.index ? strategy.index : "nifty",
      });
    }
  }, [strategy]);

  const backtestStrategy = () => {
    //console.log(extraInfo);
    const strategyWithExtraInfo = { ...strategy, ...extraInfo };
    //console.log(strategyWithExtraInfo);

    if (configData.JSON_DB === false) {
      // code only for backtest api start
      console.log("backtest request - ", strategyWithExtraInfo);
      setIsProcessing(true);
      try {
        fetch(`${configData.BACKTEST_API_URL}/run_strategies`, {
          method: "POST",
          body: JSON.stringify(strategyWithExtraInfo),
          headers: { "Content-type": "application/json; charset=UTF-8" },
        })
          .then((res) => res.json())
          .then((data) => {
            console.log("backtest response - ", data);
            setReportData({ ...data });
            setShowBackTestReport(true);
          });
      } catch (error) {
        console.error("Error receiving strategies:", error);
      } finally {
        setIsProcessing(false);
      }
      // code only for backtest api end
    } else {
      // code only for json data start
      setIsProcessing(true);
      setTimeout(() => {
        setReportData({ ...backTestReportData });
        setShowBackTestReport(true);
        setIsProcessing(false);
      }, 3000);

      // code only for json data end
    }
  };

  const onIndexChanged = (e) => {
    //console.log(e.target.value);
    setExtraInfo({ ...extraInfo, index: e.target.value });
  };

  const fromDateChanged = (e) => {
    //console.log(e.target.value);
    setExtraInfo({ ...extraInfo, fromdate: e.target.value });
  };

  const toDateChanged = (e) => {
    //console.log(e.target.value);
    setExtraInfo({ ...extraInfo, todate: e.target.value });
  };

  const showImportFileModal = () => {
    if (refImportFileModel.importFileModal) {
      if (refFileInput.current) {
        refFileInput.current.value = "";
      }
      refImportFileModel.importFileModal.show();
    }
  };

  const hideImportFileModal = () => {
    if (refImportFileModel.importFileModal) {
      refImportFileModel.importFileModal.hide();
    }
  };

  const importFile = (e) => {
    console.log(e.target.files[0]);
    const file = e.target.files[0];
    if (file) {
      var reader = new FileReader();
      reader.readAsText(file, "UTF-8");
      reader.onload = function (evt) {
        const strategy = JSON.parse(evt.target.result);
        console.log(strategy);
        hideImportFileModal();
        strategyImported(strategy);
      };
      reader.onerror = function (evt) {
        console.log("error reading file");
      };
    }
    hideImportFileModal();
  };

  const importStrategy = () => {
    showImportFileModal();
  };

  const getTodaysDate = () => {
    const dt = new Date();
    const year = dt.getFullYear().toString();
    const month = (dt.getMonth() + 1).toString();
    const day = dt.getDate().toString();
    const todaysDate =
      year +
      (month.length === 1 ? "0" + month : month) +
      (day.length === 1 ? "0" + day : day);
    return todaysDate;
  };

  const exportStrategy = () => {
    const strategyWithExtraInfo = { ...strategy, ...extraInfo };
    const blob = new Blob([JSON.stringify(strategyWithExtraInfo)], {
      type: "application/octet-stream",
    });
    saveAs(blob, `${strategy.name}_${getTodaysDate()}.json`);
  };

  return (
    <>
      <div className="back-test-strategy-content">
        {!showBackTestReport && (
          <div className="content">
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
            <div className="box leg-builder-box">
              <div className="cell save-button-row">
                <div>
                  <button
                    id="btn_import_strategy"
                    className="btn btn-light btn-import-export-strategy"
                    onClick={importStrategy}
                    disabled={isProcessing === true}
                  >
                    <span>Import Strategy</span>
                  </button>
                </div>
                <div>
                  <button
                    id="btn_export_strategy"
                    className="btn btn-light btn-import-export-strategy"
                    onClick={exportStrategy}
                    disabled={isProcessing === true}
                  >
                    <span>Export Strategy</span>
                  </button>
                </div>
                <div className="index-wrapper">
                  <label className="field-label extra-info-label">Index</label>
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
                <div className="date-input-wrapper-div">
                  <div className="date-input-wrapper">
                    <div className="extra-info-label-wrapper">
                      <label className="field-label extra-info-label">
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
                  <div className="date-input-wrapper">
                    <div className="extra-info-label-wrapper">
                      <label className="field-label extra-info-label">
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
                    id="btn_backtest_strategy"
                    className="btn theme_button"
                    onClick={backtestStrategy}
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
                    {isProcessing === false && <span>Backtest Strategy</span>}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        {showBackTestReport && (
          <div className="content">
            <BackTestReport data={reportData} />
          </div>
        )}
      </div>
      <div
        className="modal"
        tabIndex={-1}
        role="dialog"
        ref={refImportFileModel}
      >
        <div className="modal-dialog modal-dialog-centered" role="document">
          <div className="modal-content">
            <div className="modal-body">
              <div className="form-group info-modal-body">
                <div className="content">
                  <h6 className="box-title">Import Strategy file</h6>
                  <hr />
                  <input
                    type="file"
                    onChange={importFile}
                    accept=".json"
                    ref={refFileInput}
                  />
                </div>
              </div>
            </div>
            <div className="modal-footer info-modal-footer">
              <button
                type="button"
                className="btn btn-light ok-button"
                onClick={hideImportFileModal}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default BackTestStrategy;
