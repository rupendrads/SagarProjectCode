import { useEffect, useState } from "react";
import "./PortfolioDetail.css";
import { QuantityMultiplier } from "../../common/common";
import configData from "../../config.json";
import { useNavigate } from "react-router-dom";

const PortfolioDetail = (props) => {
  const [portfolio, setPortfolio] = useState(props?.portfolio);
  const navigate = useNavigate();
  console.log("props.strategies ", props.strategies);

  useEffect(() => {
    if (props.portfolio) {
      setPortfolio(props.portfolio);
    }
  }, [props.portfolio]);

  const onExecutionDayChanged = (e) => {
    console.log("is checked ", e.target.checked);
    console.log("day", e.target.id.split("-")[0]);
    console.log("strategy id", e.target.name);

    const day = e.target.id.split("-")[0];
    const strategy_id = e.target.name;
    setPortfolio((portfolio) => {
      const strategyIndex = portfolio.strategies.findIndex(
        (strategy) => strategy.strategy_id == strategy_id
      );
      console.log("strategyIndex ", strategyIndex);
      if (strategyIndex > -1) {
        console.log(portfolio.strategies[strategyIndex][day]);
        portfolio.strategies[strategyIndex][day] =
          e.target.checked == true ? true : false;

        console.log(portfolio.strategies[strategyIndex][day]);
      }
      console.log(portfolio);
      return { ...portfolio };
    });
  };

  const onSymbolChanged = (e) => {
    const strategy_id = e.target.id.split("-")[0];
    setPortfolio((portfolio) => {
      const strategyIndex = portfolio.strategies.findIndex(
        (strategy) => strategy.strategy_id == strategy_id
      );
      console.log("strategyIndex ", strategyIndex);
      if (strategyIndex > -1) {
        console.log(portfolio.strategies[strategyIndex].symbol);
        portfolio.strategies[strategyIndex].symbol = e.target.value;
        portfolio.strategies[strategyIndex].quantity_multiplier =
          QuantityMultiplier[e.target.value];
      }
      console.log(portfolio);
      return { ...portfolio };
    });
  };

  const getStrategyName = (strategy_id) => {
    let strategyName = "Not found";
    if (props.strategies) {
      const strategy = props.strategies.find((s) => s.id == strategy_id);
      if (strategy) {
        strategyName = strategy.name;
      }
    }
    return strategyName;
  };

  const updatePortfolio = async () => {
    console.log(portfolio);
    try {
      const response = await fetch(
        `${configData.API_URL}/portfolios/${portfolio.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(portfolio),
        }
      );
      const data = await response.json();
      console.log("Update response - ", data);
      props.refreshPortfolioList();
    } catch (error) {
      console.error("Error updating portfolio:", error);
    } finally {
    }
  };

  const strategyNameClick = (id) => {
    navigate(`/strategy/${id}`);
  };

  const showStrategyVariables = (portfolio_strategy_id) => {
    props.showStrategyVariables(portfolio_strategy_id);
  };

  return (
    <>
      {props === undefined && <h5>Please select portfolio to see details</h5>}
      {portfolio && (
        <div className="content">
          <div className="box">
            <div className="cell flex-row portfolio-detail-header">
              <div>
                <h6 className="box-title">
                  Portfolio Detail - {portfolio.name}
                </h6>
              </div>
              <div>
                <button
                  className="btn theme_button"
                  onClick={props.editPortfolio}
                >
                  Edit Portfolio
                </button>
              </div>
            </div>
            <div className="cell">
              <table class="table table-striped table-hover">
                <thead>
                  <tr>
                    <th scope="col">No</th>
                    <th scope="col">Strategy</th>
                    <th scope="col">Symbol</th>
                    <th scope="col">Quantity Multiplier</th>
                    <th scope="col">Execution Days</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.strategies &&
                    portfolio.strategies.map((strategy, index) => {
                      return (
                        <tr>
                          <th scope="row">{index + 1}</th>
                          <td>
                            <div
                              className="portfolio-strategy-name-link"
                              onClick={() =>
                                strategyNameClick(strategy.strategy_id)
                              }
                            >
                              {getStrategyName(strategy.strategy_id)}
                            </div>
                          </td>
                          <td>
                            <select
                              id={`${strategy.strategy_id}-symbol`}
                              name={`${strategy.strategy_id}-symbol`}
                              value={strategy.symbol}
                              className="form-select"
                              onChange={onSymbolChanged}
                            >
                              <option value="nifty">Nifty</option>
                              <option value="banknifty">Banknifty</option>
                              <option value="finnifty">Finnifty</option>
                            </select>
                          </td>
                          <td>{strategy.quantity_multiplier}</td>
                          <td>
                            <input
                              type="checkbox"
                              className="btn-check"
                              name={strategy.strategy_id}
                              id={`monday-${strategy.strategy_id}`}
                              autocomplete="off"
                              checked={strategy.monday == true}
                              value={strategy.monday}
                              onChange={onExecutionDayChanged}
                            />
                            <label
                              className="btn btn-outline-success rounded-0"
                              for={`monday-${strategy.strategy_id}`}
                            >
                              M
                            </label>
                            <input
                              type="checkbox"
                              className="btn-check"
                              name={strategy.strategy_id}
                              id={`tuesday-${strategy.strategy_id}`}
                              autocomplete="off"
                              checked={strategy.tuesday == true}
                              value={strategy.tuesday}
                              onChange={onExecutionDayChanged}
                            />
                            <label
                              className="btn btn-outline-success rounded-0"
                              for={`tuesday-${strategy.strategy_id}`}
                            >
                              T
                            </label>
                            <input
                              type="checkbox"
                              className="btn-check"
                              name={strategy.strategy_id}
                              id={`wednesday-${strategy.strategy_id}`}
                              autocomplete="off"
                              checked={strategy.wednesday == true}
                              value={strategy.wednesday}
                              onChange={onExecutionDayChanged}
                            />
                            <label
                              className="btn btn-outline-success rounded-0"
                              for={`wednesday-${strategy.strategy_id}`}
                            >
                              W
                            </label>
                            <input
                              type="checkbox"
                              className="btn-check"
                              name={strategy.strategy_id}
                              id={`thrusday-${strategy.strategy_id}`}
                              autocomplete="off"
                              checked={strategy.thrusday == true}
                              value={strategy.thrusday}
                              onChange={onExecutionDayChanged}
                            />
                            <label
                              className="btn btn-outline-success rounded-0"
                              for={`thrusday-${strategy.strategy_id}`}
                            >
                              Th
                            </label>
                            <input
                              type="checkbox"
                              className="btn-check"
                              name={strategy.strategy_id}
                              id={`friday-${strategy.strategy_id}`}
                              autocomplete="off"
                              checked={strategy.friday == true}
                              value={strategy.friday}
                              onChange={onExecutionDayChanged}
                            />
                            <label
                              className="btn btn-outline-success rounded-0"
                              for={`friday-${strategy.strategy_id}`}
                            >
                              F
                            </label>
                          </td>
                          <td>
                            <button
                              className="btn btn-secondary"
                              onClick={() => showStrategyVariables(strategy.id)}
                            >
                              Variables
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>
            <div className="cell portfolio-update-button-div">
              <button className="btn theme_button" onClick={updatePortfolio}>
                Update Portfolio
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PortfolioDetail;
