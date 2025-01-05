import Leg from "./leg/Leg";
import "./OptimizationVariables.css";
import OverallStrategy from "./overallStrategy/OverallStrategy";

const OptimizationVariables = (props) => {
  const {
    optimizationParameters,
    onChangeOptimizationParameters,
    onChangeLegs,
  } = props;
  //console.log(onChangeLegs);
  return (
    <div className="optimization-strategy-vaiables-content">
      <div className="box overall-strategy-box">
        <OverallStrategy
          optimizationParameters={optimizationParameters.overallStrategy}
          onChangeOptimizationParameters={onChangeOptimizationParameters}
        />
      </div>
      <div className="box leg-builder-box">
        <div className="cell">
          <h6 className="box-title">Legs</h6>
          <hr />
        </div>
        {
          <>
            {optimizationParameters.legs.map((leg, index) => {
              return <Leg key={leg.id} leg={leg} onChangeLegs={onChangeLegs} />;
            })}
          </>
        }
      </div>
    </div>
  );
};
export default OptimizationVariables;
