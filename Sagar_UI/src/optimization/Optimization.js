import { useState } from "react";
import OptimizationStrategy from "./optimizationStrategy/OptimizationStrategy";
import Sidebar from "./sidebar/Sidebar";
import configData from "../config.json";
import "./Optimization.css";

const Optimization = () => {
  const [strategy, setStrategy] = useState(undefined);

  const showStrategy = (e) => {
    console.log(e.id);
    //console.log(`${configData.API_URL}/strategies/${e.id}`);
    if (e.id !== undefined) {
      try {
        fetch(`${configData.API_URL}/strategies/${e.id}`)
          .then((res) => {
            //console.log(res);
            if (res.ok === true) return res.json();
            else throw new Error("Status code error :" + res.status);
          })
          .then((data) => {
            //console.log("existing data - ", data);
            setStrategy(data);
          })
          .catch((error) => console.error("Error receiving strategy:", error));
      } catch (error) {
        console.error("Error receiving strategy:", error);
      }
    }
  };

  return (
    <>
      <div className="sidebar">
        <Sidebar showStrategy={showStrategy} />
      </div>
      {strategy ? (
        <OptimizationStrategy strategy={strategy} />
      ) : (
        <OptimizationStrategy />
      )}
    </>
  );
};

export default Optimization;
