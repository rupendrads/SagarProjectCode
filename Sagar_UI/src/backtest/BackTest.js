import { useState } from "react";
import BackTestStrategy from "./backtestStrategy/BackTestStrategy";
import Sidebar from "./sidebar/Sidebar";
import configData from "../config.json";

const BackTest = () => {
  const [strategy, setStrategy] = useState(undefined);

  const showStrategy = (e) => {
    console.log(e.id);
    console.log(`${configData.API_URL}/strategies/${e.id}`);
    if (e.id !== undefined) {
      try {
        fetch(`${configData.API_URL}/strategies/${e.id}`)
          .then((res) => {
            console.log(res);
            if (res.ok === true) return res.json();
            else throw new Error("Status code error :" + res.status);
          })
          .then((data) => {
            console.log("existing data - ", data);
            setStrategy(data);
          })
          .catch((error) => console.error("Error receiving strategy:", error));
      } catch (error) {
        console.error("Error receiving strategy:", error);
      }
    }
  };

  const strategyImported = (strategy) => {
    console.log("imported strategy", strategy);
    setStrategy(strategy);
  };

  return (
    <>
      <div className="sidebar">
        <Sidebar showStrategy={showStrategy} />
      </div>
      {strategy && (
        <BackTestStrategy
          strategy={strategy}
          strategyImported={strategyImported}
        />
      )}
    </>
  );
};

export default BackTest;
