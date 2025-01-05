import { useState, useEffect } from "react";
import Sidebar from "./sidebar/Sidebar";
import AddPortfolio from "./AddPortfolio/AddPortfolio";
import PortfolioDetail from "./portfolioDetail/PortfolioDetail";
import EditPortfolio from "./EditPortfolio/EditPortfolio";
import configData from "../config.json";
import { PortfolioStrategy } from "./portfolioStrategy/PortfolioStrategy";

const Portfolio = () => {
  const [content, setContent] = useState("list");
  const [refreshList, setRefreshList] = useState(false);
  const [portfolio, setPortfolio] = useState(undefined);
  const [strategies, setStrategies] = useState([]);
  const [strategyVariables, setStrategyVariables] = useState({});
  const [id, setId] = useState();

  useEffect(() => {
    try {
      if (id) {
        fetch(`${configData.API_URL}/portfolios/${id}`)
          .then((res) => res.json())
          .then((data) => {
            console.log("id - ", id);
            console.log("response - ", data);
            if (data) {
              setPortfolio(data);
            }
          });
      }
    } catch (error) {
      console.error("Error receiving portfolio:", error);
    }
  }, [id]);

  useEffect(() => {
    try {
      fetch(`${configData.API_URL}/portfolios`)
        .then((res) => res.json())
        .then((data) => {
          console.log("response - ", data);
          if (data.length > 0) {
            setId((prevId) => {
              try {
                if (prevId == data[0].id) {
                  fetch(`${configData.API_URL}/portfolios/${data[0].id}`)
                    .then((res) => res.json())
                    .then((data) => {
                      console.log("id - ", id);
                      console.log("response - ", data);
                      if (data) {
                        setPortfolio(data);
                      }
                    });
                }
              } catch (error) {
              } finally {
                return data[0].id;
              }
            });
          }
        });
    } catch (error) {
      console.error("Error receiving portfolio:", error);
    }
  }, [refreshList]);

  useEffect(() => {
    try {
      fetch(`${configData.API_URL}/strategies`)
        .then((res) => res.json())
        .then((data) => {
          console.log("response - ", data);
          console.log(portfolio);
          setStrategies(data);
        });
    } catch (error) {
      console.error("Error receiving strategies:", error);
    }
  }, []);

  const addPortfolio = () => {
    setContent("add");
  };

  const editPortfolio = () => {
    console.log("id - ", id);
    setContent("edit");
  };

  const refreshPortfolioList = () => {
    setContent("list");
    setRefreshList(!refreshList);
  };

  const cancelPortfolioEdit = () => {
    setContent("list");
  };

  const cancelPortfolioAdd = () => {
    setContent("list");
  };

  const ShowPortfolio = (e) => {
    console.log("id - ", e.id);
    setId(e.id);
  };

  const showStrategyVariables = (portfolio_strategy_id) => {
    console.log(portfolio_strategy_id);
    const portfolioStrategy = portfolio.strategies.find(
      (s) => s.id == portfolio_strategy_id
    );
    console.log(portfolioStrategy.strategyvariables);
    const strategy = strategies.find(
      (s) => s.id === portfolioStrategy.strategy_id
    );

    setStrategyVariables({
      ...portfolioStrategy.strategyvariables,
      strategy_name: strategy.name,
    });
    setContent("variables");
  };

  const updateStrategyVariables = async (strategy_variables) => {
    ////////// code only for json update start ////////////////////
    // console.log(portfolio);
    // const portfolio_strategy_id = strategy_variables.portfolio_strategy_id;
    // const portfolioStrategyIndex = portfolio.strategies.findIndex(
    //   (s) => s.id == portfolio_strategy_id
    // );
    // if (portfolioStrategyIndex !== -1) {
    //   const updatedStrategies = [...portfolio.strategies];
    //   updatedStrategies.splice(portfolioStrategyIndex, 1, {
    //     ...portfolio.strategies[portfolioStrategyIndex],
    //     strategyvariables: strategy_variables,
    //   });
    //   console.log(updatedStrategies);
    //   const updatedPortfolio = { ...portfolio, strategies: updatedStrategies };
    //   console.log(updatedPortfolio);
    //   try {
    //     const response = await fetch(
    //       `${configData.API_URL}/portfolios/${portfolio.id}`,
    //       {
    //         method: "PUT",
    //         headers: {
    //           "Content-Type": "application/json",
    //         },
    //         body: JSON.stringify(updatedPortfolio),
    //       }
    //     );
    //     const data = await response.json();
    //     console.log("Update strategy variables response - ", data);
    //     setPortfolio(updatedPortfolio);
    //   } catch (error) {
    //     console.error("Error updating portfolio strategy variables:", error);
    //   } finally {
    //   }
    //}
    /////// code only for json update end //////////////////////

    ////// code for api update start //////////////////////////
    console.log(strategy_variables);
    strategy_variables.legs.forEach((leg) => {
      if (leg.id - Math.floor(leg.id) !== 0) {
        leg.id = 0;
      }
    });
    console.log(strategy_variables);
    try {
      const response = await fetch(
        `${configData.API_URL}/strategyvariables/${strategy_variables.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(strategy_variables),
        }
      );
      const data = await response.json();
      console.log("Update strategy variables response - ", data);
      console.log("changing portfolio", portfolio);

      const portfolioStrategies = [...portfolio.strategies];
      portfolioStrategies.map((ps) => {
        if (ps.strategyvariables.id === data.id) {
          ps.strategyvariables = { ...data };
        }
      });
      console.log("portfolioStrategies", portfolioStrategies);
      setPortfolio({ ...portfolio, strategies: portfolioStrategies });

      console.log("setting content");
      setContent("list");
    } catch (error) {
      console.error("Error updating portfolio strategy variables:", error);
    } finally {
    }

    ////// code for api update end //////////////////////////
  };

  const isContent =
    content === "list" && strategies.length > 0 && portfolio !== undefined;

  const backToPortfolio = () => {
    setContent("list");
  };

  return (
    <>
      <div
        className="sidebar"
        disabled={
          content === "add" || content === "edit" || content === "variables"
        }
      >
        <Sidebar
          addPortfolio={addPortfolio}
          ShowPortfolio={ShowPortfolio}
          refreshList={refreshList}
        />
      </div>
      <div className="content">
        {isContent && (
          <PortfolioDetail
            portfolio={portfolio}
            editPortfolio={editPortfolio}
            strategies={strategies}
            refreshPortfolioList={refreshPortfolioList}
            showStrategyVariables={showStrategyVariables}
          />
        )}
        {content === "add" && (
          <AddPortfolio
            refreshPortfolioList={refreshPortfolioList}
            strategies={strategies}
            cancelPortfolioAdd={cancelPortfolioAdd}
          />
        )}
        {content === "edit" && (
          <EditPortfolio
            portfolio={portfolio}
            strategies={strategies}
            refreshPortfolioList={refreshPortfolioList}
            cancelPortfolioEdit={cancelPortfolioEdit}
          />
        )}
        {content === "variables" && (
          <PortfolioStrategy
            portfolioStrategy={strategyVariables}
            updatePortfolioStrategy={updateStrategyVariables}
            portfolioName={portfolio.name}
            backToPortfolio={backToPortfolio}
          />
        )}
      </div>
    </>
  );
};

export default Portfolio;
