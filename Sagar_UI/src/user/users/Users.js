import { useEffect, useState } from "react";
import Sidebar from "../sidebar/Sidebar";
import "./Users.css";
import Registration from "../registration/Registration";
import configData from "../../config.json";

const Users = () => {
  const [user, setUser] = useState();
  const [newUser, setNewUser] = useState(true);
  const [step, setStep] = useState(1);
  const [stepItems, setStepItems] = useState([
    {
      step: 1,
      name: "User details",
      completed: false,
    },
    {
      step: 2,
      name: "Billing",
      completed: false,
    },
    {
      step: 3,
      name: "Access Modules",
      completed: false,
    },
    {
      step: 4,
      name: "Brokers",
      completed: false,
    },
  ]);

  const forwardStep = () => {
    setStep(step + 1);
  };

  const changeStep = (stepNumber) => {
    setStep(stepNumber);
  };

  const showUser = (user) => {
    setNewUser(false);
    setStep(1);

    let urlSegment = "user";

    if (configData.JSON_DB === false) {
      urlSegment = "getUser";
    }

    try {
      fetch(`${configData.API_URL}/${urlSegment}/${user.id}`, {
        method: "GET",
        headers: { "Content-type": "application/json; charset=UTF-8" },
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("user response - ", data);
          setUser(data);
          setStepItems((prev) => {
            const items = prev.map((i) => {
              if (i.step === 1) {
                i.completed = true;
              }
              return i;
            });
            console.log(items);
            return items;
          });
        });
    } catch (error) {
      console.error("Error retriving user list:", error);
    } finally {
    }
  };

  const registerUser = () => {
    setUser();
    setNewUser(true);
    setStep(1);
  };

  const storeUser = (user) => {
    console.log("storing user", user);
    setUser(user);
  };

  return (
    <>
      <div className="sidebar">
        <Sidebar showUser={showUser} registerUser={registerUser} />
        <div>{console.log(newUser)}</div>
      </div>
      {!newUser && (
        <Registration
          isNewUser={newUser}
          user={user}
          step={step}
          stepItems={stepItems}
          changeStep={changeStep}
        />
      )}
      {newUser && (
        <Registration
          isNewUser={newUser}
          user={user}
          storeUser={storeUser}
          step={step}
          forwardStep={forwardStep}
          stepItems={stepItems}
        />
      )}
    </>
  );
};

export default Users;
