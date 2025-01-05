import { useEffect, useState } from "react";
import "./Sidebar.css";
import configData from "../../config.json";

const Sidebar = ({ addPortfolio, ShowPortfolio, refreshList }) => {
  const [portfolioList, setPortfolioList] = useState([]);

  useEffect(() => {
    try {
      fetch(`${configData.API_URL}/portfolios`)
        .then((res) => res.json())
        .then((data) => {
          console.log("response - ", data);
          let namesData = [];
          data.map((item) => {
            namesData.push({
              id: item.id,
              name: item.name,
            });
          });
          console.log("namesData - ", namesData);
          setPortfolioList(namesData);
        });
    } catch (error) {
      console.error("Error receiving portfolios:", error);
    }
  }, [refreshList]);

  return (
    <>
      <div className="card">
        <div className="card card-body">
          <div className="cell">
            <button className="btn theme_button" onClick={() => addPortfolio()}>
              New Portfolio
            </button>
          </div>
          <hr />
          <div className="card-title" style={{ fontWeight: "600" }}>
            <label>Existing Portfolios</label>
          </div>
          <div className="cell">
            <ul class="nav flex-column portfolio-list">
              {portfolioList.map((portfolio) => (
                <li
                  className="nav-item link"
                  key={portfolio.id}
                  onClick={() => ShowPortfolio({ id: portfolio.id })}
                  style={{ cursor: "" }}
                >
                  {portfolio.name}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </>
  );
};
export default Sidebar;
