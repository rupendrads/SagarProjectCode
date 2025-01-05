import { useState, useEffect } from "react";
import Leg from "../../strategy/Leg/Leg";
import { defaultLeg } from "../../strategy/Leg/defaultLeg";
import { OverallStrategy } from "../../strategy/overallstrategy/OverallStrategy";
import "./PortfolioStrategy.css";

export const PortfolioStrategy = (props) => {
  const {
    portfolioStrategy,
    updatePortfolioStrategy,
    portfolioName,
    backToPortfolio,
  } = props;

  const [overallStrategy, setOverallStrategy] = useState({});
  const [legs, setLegs] = useState([]);

  useEffect(() => {
    if (portfolioStrategy !== undefined) {
      console.log("portfolio strategy - ", portfolioStrategy);
      setOverallStrategy({
        id: portfolioStrategy.id,
        name: portfolioStrategy.strategy_name,
        underlying: portfolioStrategy.underlying,
        strategy_type: portfolioStrategy.strategy_type,
        implied_futures_expiry: portfolioStrategy.implied_futures_expiry,
        entry_time: portfolioStrategy.entry_time,
        last_entry_time: portfolioStrategy.last_entry_time,
        exit_time: portfolioStrategy.exit_time,
        square_off: portfolioStrategy.square_off,
        overall_sl: portfolioStrategy.overall_sl,
        overall_target: portfolioStrategy.overall_target,
        trailing_options: portfolioStrategy.trailing_options,
        profit_reaches: portfolioStrategy.profit_reaches,
        lock_profit: portfolioStrategy.lock_profit,
        increase_in_profit: portfolioStrategy.increase_in_profit,
        trail_profit: portfolioStrategy.trail_profit,
      });

      console.log("legs -", portfolioStrategy.legs);
      setLegs([...portfolioStrategy.legs]);
    }
  }, []);

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

  const addLeg = (e) => {
    console.log(legs);
    const newDefaultLeg = { ...defaultLeg };
    newDefaultLeg.id = (Math.random() + 1).toString();
    setLegs((prevLegs) => [...prevLegs, { ...newDefaultLeg }]);
  };

  const removeLeg = (id) => {
    console.log("removing leg");
    setLegs((prevLegs) => {
      const newLegs = prevLegs.filter((leg) => {
        return leg.id != id;
      });
      return [...newLegs];
    });
  };

  const getFormData = () => {
    const updatedLegs = [...legs];
    updatedLegs.map((leg) => {
      leg["portfolio_strategy_variables_id"] = portfolioStrategy.id;
    });
    const strategy = {
      id: overallStrategy.id,
      portfolio_strategy_id: portfolioStrategy.portfolio_strategy_id,
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

  const saveStrategy = async () => {
    console.log("saving strategy");
    const updatedPortfolioStrategy = getFormData();
    console.log("modified portfolio strategy", updatedPortfolioStrategy);
    updatePortfolioStrategy(updatedPortfolioStrategy);
  };

  return (
    <div className="content">
      <div className="box overall-strategy-box">
        <div className="back-to-portfolio-wrapper">
          <button className="btn theme_button" onClick={backToPortfolio}>
            <span>Back to Portfolio</span>
          </button>
        </div>
        <OverallStrategy
          overallStrategy={overallStrategy}
          onChangeOverallStrategy={onChangeOverallStrategy}
        >
          <span>{` - ${portfolioName}`}</span>
        </OverallStrategy>
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
          <button className="btn theme_button" onClick={saveStrategy}>
            Update Strategy
          </button>
        </div>
      </div>
    </div>
  );
};
