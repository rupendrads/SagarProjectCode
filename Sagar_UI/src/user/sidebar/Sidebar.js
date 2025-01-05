import { useEffect, useState } from "react";
import "./Sidebar.css";
import configData from "../../config.json";

const Sidebar = (props) => {
  const { showUser, registerUser } = props;
  const [userNames, setUserNames] = useState([]);

  useEffect(() => {
    let urlSegment = "user";

    if (configData.JSON_DB === false) {
      urlSegment = "getAllUsers";
    }

    try {
      fetch(`${configData.API_URL}/${urlSegment}`)
        .then((res) => res.json())
        .then((data) => {
          console.log("user list", data);
          let namesData = [];
          data.map((item) => {
            namesData.push({
              id: item.id,
              name: item.first_name + " " + item.last_name,
            });
          });
          setUserNames([...namesData]);
        });
    } catch (error) {
      console.error("Error receiving users:", error);
    }
  }, []);

  return (
    <>
      <div className="card" id="timebased">
        <div
          className="card-title"
          style={{ fontWeight: "600", padding: "10px" }}
        >
          <button
            className="btn theme_button"
            type="button"
            onClick={registerUser}
          >
            User Registration
          </button>
        </div>

        <div className="card card-body">
          <div className="card-title" style={{ fontWeight: "600" }}>
            <label>Existing Users</label>
            <hr className="strategy-sidebar-hr" />
          </div>
          <ul class="nav flex-column strategy-list">
            {userNames.map((user) => (
              <li
                className="nav-item link"
                key={user.id}
                onClick={() => showUser({ id: user.id })}
                style={{ cursor: "" }}
              >
                {user.name}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
};
export default Sidebar;
