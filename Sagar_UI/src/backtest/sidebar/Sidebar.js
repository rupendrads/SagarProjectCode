import { useEffect, useState } from "react";
import "./Sidebar.css";
import configData from "../../config.json";

const Sidebar = (props) => {
  const { showStrategy } = props;
  const [strategyNames, setStrategyNames] = useState([]);

  useEffect(() => {
    try {
      fetch(`${configData.API_URL}/strategies`)
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
          setStrategyNames([...namesData]);
        });
    } catch (error) {
      console.error("Error receiving strategies:", error);
    }
  }, []);

  return (
    <>
      {console.log("rendering...")}
      <div className="card" id="timebased">
        <div
          className="card-title"
          style={{ fontWeight: "600", padding: "10px" }}
        >
          <label>Time based Strategies</label>
        </div>

        <div className="card card-body">
          <div className="card-title" style={{ fontWeight: "600" }}>
            <label>Existing Strategies</label>
            <hr className="strategy-sidebar-hr" />
          </div>
          <ul class="nav flex-column strategy-list">
            {strategyNames.map((strategy) => (
              <li
                className="nav-item link"
                key={strategy.id}
                onClick={() => showStrategy({ id: strategy.id })}
                style={{ cursor: "" }}
              >
                {strategy.name}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
};
export default Sidebar;
