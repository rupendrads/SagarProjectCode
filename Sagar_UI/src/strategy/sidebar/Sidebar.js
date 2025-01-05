import { useEffect, useState } from "react";
import "./Sidebar.css";
import { useNavigate } from "react-router-dom";
import configData from "../../config.json";

const Sidebar = (props) => {
  const [strategyNames, setStrategyNames] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    try {
      fetch(`${configData.API_URL}/strategies`)
        .then((res) => res.json())
        .then((data) => {
          console.log("response - ", data);
          let namesData = [];
          data.map((item) => {
            console.log("item", item);
            namesData.push({
              id: item.id,
              name: item.name,
            });
          });
          console.log("namesData - ", namesData);
          setStrategyNames(namesData);
        });
    } catch (error) {
      console.error("Error receiving strategies:", error);
    }
  }, [props.refresh]);

  const showStrategy = (e) => {
    console.log(e.id);
    navigate(`/strategy/${e.id}`);
  };

  const newStrategy = () => {
    navigate("/strategy/");
  };

  return (
    <>
      <div className="card" id="timebased">
        <div
          className="card-title"
          style={{ fontWeight: "600", padding: "10px" }}
        >
          <label>Time based Strategies</label>
        </div>

        <div className="card card-body">
          <div className="cell new-strategy">
            <button className="btn theme_button" onClick={newStrategy}>
              New Strategy
            </button>
          </div>
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
