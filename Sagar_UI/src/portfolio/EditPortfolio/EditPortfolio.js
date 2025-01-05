import { useEffect, useState } from "react";
import { QuantityMultiplier } from "../../common/common";
import configData from "../../config.json";

const EditPortfolio = (props) => {
  const [strategyNames, setStrategyNames] = useState([]);
  const [portfolio, setPortfolio] = useState({});

  useEffect(() => {
    if (props.portfolio) {
      console.log("setting portfolio");
      console.log("existing portfolio in useEffect ", props.portfolio);
      setPortfolio(props.portfolio);
    }
  }, [props.portfolio]);

  useEffect(() => {
    if (props.portfolio && props.strategies) {
      console.log("setting strategy names");
      let selectedIds = [];
      props.portfolio.strategies.map((strategy) => {
        selectedIds.push(strategy.strategy_id);
      });
      let namesData = [];
      props.strategies.map((item) => {
        namesData.push({
          id: item.id,
          name: item.name,
          checked: selectedIds.includes(item.id),
        });
      });
      setStrategyNames(namesData);
    }
  }, [props.portfolio, props.strategies]);

  const onPortfolioNameChanged = (e) => {
    setPortfolio({ ...portfolio, name: e.target.value });
  };

  const getFormData = () => {
    console.log("existing portfolio - ", portfolio);
    let portfolioUpdated = { ...portfolio };

    let strategies = [];
    console.log("strategy names - ", strategyNames);
    strategyNames.map((strategyName) => {
      if (strategyName.checked === true) {
        console.log("selected strategy - ", strategyName);
        const strategyIndex = portfolio.strategies.findIndex(
          (strategy) => strategy.strategy_id == strategyName.id
        );
        console.log("is existing - ", strategyIndex != -1);

        console.log("pushing new strategy");
        if (strategyIndex === -1) {
          let strategyVariables = {};
          const portfolioStrategyId = Math.random() + 1;
          const strategy = props.strategies.find(
            (s) => s.id == strategyName.id
          );
          if (strategy) {
            let legs = [];
            const portfolioStrategyVariablesId = Math.random() + 1;

            strategy.legs.map((leg) => {
              const legId = Math.random() + 1;
              legs.push({
                id: legId,
                portfolio_strategy_variables_id: portfolioStrategyVariablesId,
                lots: leg.lots,
                position: leg.position,
                option_type: leg.option_type,
                expiry: leg.expiry,
                no_of_reentry: leg.no_of_reentry,
                strike_selection_criteria: leg.strike_selection_criteria,
                closest_premium: leg.closest_premium,
                strike_type: leg.strike_type,
                straddle_width_value: leg.straddle_width_value,
                straddle_width_sign: leg.straddle_width_sign,
                percent_of_atm_strike_value: leg.percent_of_atm_strike_value,
                percent_of_atm_strike_sign: leg.percent_of_atm_strike_sign,
                atm_straddle_premium: leg.atm_straddle_premium,
                strike_selection_criteria_stop_loss:
                  leg.strike_selection_criteria_stop_loss,
                strike_selection_criteria_stop_loss_sign:
                  leg.strike_selection_criteria_stop_loss_sign,
                strike_selection_criteria_trailing_options:
                  leg.strike_selection_criteria_trailing_options,
                strike_selection_criteria_profit_reaches:
                  leg.strike_selection_criteria_profit_reaches,
                strike_selection_criteria_lock_profit:
                  leg.strike_selection_criteria_lock_profit,
                strike_selection_criteria_lock_profit_sign:
                  leg.strike_selection_criteria_lock_profit_sign,
                strike_selection_criteria_increase_in_profit:
                  leg.strike_selection_criteria_increase_in_profit,
                strike_selection_criteria_trail_profit:
                  leg.strike_selection_criteria_trail_profit,
                strike_selection_criteria_trail_profit_sign:
                  leg.strike_selection_criteria_trail_profit_sign,
                roll_strike: leg.roll_strike,
                roll_strike_strike_type: leg.roll_strike_strike_type,
                roll_strike_stop_loss: leg.roll_strike_stop_loss,
                roll_strike_stop_loss_sign: leg.roll_strike_stop_loss_sign,
                roll_strike_trailing_options: leg.roll_strike_trailing_options,
                roll_strike_profit_reaches: leg.roll_strike_profit_reaches,
                roll_strike_lock_profit: leg.roll_strike_lock_profit,
                roll_strike_lock_profit_sign: leg.roll_strike_lock_profit_sign,
                roll_strike_increase_in_profit:
                  leg.roll_strike_increase_in_profit,
                roll_strike_trail_profit: leg.roll_strike_trail_profit,
                roll_strike_trail_profit_sign:
                  leg.roll_strike_trail_profit_sign,
                simple_momentum_range_breakout:
                  leg.simple_momentum_range_breakout,
                simple_momentum: leg.simple_momentum,
                simple_momentum_sign: leg.simple_momentum_sign,
                simple_momentum_direction: leg.simple_momentum_direction,
                range_breakout: leg.range_breakout,
              });
            });

            strategyVariables = {
              id: portfolioStrategyVariablesId,
              portfolio_strategy_id: portfolioStrategyId,
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
              legs: [...legs],
            };

            strategies.push({
              id: portfolioStrategyId,
              portfolio_id: portfolio.id,
              strategy_id: strategyName.id,
              symbol: "nifty",
              quantity_multiplier: QuantityMultiplier.nifty,
              monday: false,
              tuesday: false,
              wednesday: false,
              thrusday: false,
              friday: false,
              strategyvariables: { ...strategyVariables },
            });
          }
        } else {
          console.log("pushing existing strategy");
          strategies.push({ ...portfolio.strategies[strategyIndex] });
        }
      }
    });

    portfolioUpdated.strategies = [...strategies];

    return portfolioUpdated;
  };

  const onSavePortfolio = async () => {
    const portfolio = getFormData();
    console.log("updated portfolio - ", portfolio);
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
      console.log("Modification response - ", data);
      props.refreshPortfolioList();
    } catch (error) {
      console.error("Error modifying portfolio:", error);
    } finally {
    }
  };

  const onCancelPortfolioEdit = () => {
    props.cancelPortfolioEdit();
  };

  const onStrategySelectionToggle = (event) => {
    const checkedId = event.target.value;
    setStrategyNames((prev) => {
      let newNames = [];
      for (let i = 0; i < prev.length; i++) {
        newNames.push({
          id: prev[i].id,
          name: prev[i].name,
          checked: prev[i].id == checkedId ? !prev[i].checked : prev[i].checked,
        });
      }
      return [...newNames];
    });
  };

  return (
    <>
      <div className="content">
        <div className="box add-edit-portfolio-box">
          <div className="cell">
            <h6 className="box-title">Edit Portfolio</h6>
            <hr />
          </div>
          <div className="box-content-fill">
            <div className="box card" style={{ flexDirection: "column" }}>
              <div className="cell">
                <label htmlFor="portfolioName" className="field-label">
                  Portfolio Name
                </label>
                <input
                  type="text"
                  className="form-control"
                  id="portfolioName"
                  name="portfolioName"
                  value={portfolio.name}
                  onChange={onPortfolioNameChanged}
                ></input>
              </div>
              <div className="cell">
                <label className="field-label">Portfolio Strategies</label>
              </div>
              <div className="cell">
                {strategyNames &&
                  strategyNames.map((strategy) => (
                    <div class="form-check">
                      <input
                        class="form-check-input"
                        type="checkbox"
                        value={strategy.id}
                        id={strategy.id}
                        onChange={onStrategySelectionToggle}
                        checked={strategy.checked}
                      />
                      <label class="form-check-label" for={strategy.id}>
                        {strategy.name}
                      </label>
                    </div>
                  ))}
              </div>
              <div className="cell">
                <button className="btn theme_button" onClick={onSavePortfolio}>
                  Save Portfolio
                </button>
                <button
                  className="btn btn-secondary btn-cancel"
                  onClick={onCancelPortfolioEdit}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default EditPortfolio;
