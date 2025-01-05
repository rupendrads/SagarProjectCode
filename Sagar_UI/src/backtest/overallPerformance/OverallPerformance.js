import { useEffect } from "react";
import { Tooltip } from "bootstrap/dist/js/bootstrap.min";
import "./OverallPerformance.css";

export const OverallPerformance = (props) => {
  const { overallPerformance } = props;

  useEffect(() => {
    document
      .querySelectorAll('[data-bs-toggle="tooltip"]')
      .forEach((tooltip) => {
        new Tooltip(tooltip);
      });
  }, []);

  return (
    <>
      <div className="cell overallperformance-header">
        <h6 className="box-title">Overall Performance</h6>
      </div>
      <div className="box card">
        <div className="overallperformance-row">
          <div className="overallperformance-cell">
            <div
              data-bs-toggle="tooltip"
              data-bs-title="Without deducting brokerage, taxes and slippages"
            >
              <label className="field-label">Total Profit</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.TotalProfit}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div>
              <label className="field-label">Max Profit in Single Trade</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.MaxProfitInSingleTrade}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div
              data-bs-toggle="tooltip"
              data-bs-title="Max (No of Consecutive  Days in Profit)"
            >
              <label className="field-label">Max Winning Streak (trades)</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.MaxWinningStreak}
              </label>
            </div>
          </div>
        </div>
        <div className="overallperformance-row">
          <div className="overallperformance-cell">
            <div
              data-bs-toggle="tooltip"
              data-bs-title="After deducting all brokerage, taxes and slippages"
            >
              <label className="field-label">Net Profit</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.NetProfit}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div>
              <label className="field-label">Max Loss in Single Trade</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.MaxLossInSingleTrade}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div>
              <label className="field-label">Max DD Period</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.MaxDDPeriod}
              </label>
            </div>
          </div>
        </div>
        <div className="overallperformance-row">
          <div className="overallperformance-cell">
            <div
              data-bs-toggle="tooltip"
              data-bs-title="Summation of all days in profit"
            >
              <label className="field-label">Overall Profit</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.OverallProfit}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div data-bs-toggle="tooltip" data-bs-title="Number of days trades">
              <label className="field-label">Total Trading Days</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.TotalTradingDays}
              </label>
            </div>
          </div>
          <div
            className="overallperformance-cell"
            style={{ justifyContent: "flex-start" }}
          >
            <div
              style={{
                flex: "1",
              }}
            >
              <label className="field-label">Duration at Max Drawdown</label>
            </div>
            <div>
              <label className="field-label">
                {`${overallPerformance.DurationOfMaxDrawdown.days}
                [${overallPerformance.DurationOfMaxDrawdown.start} to 
                ${overallPerformance.DurationOfMaxDrawdown.end}]`}
              </label>
            </div>
          </div>
        </div>
        <div className="overallperformance-row">
          <div className="overallperformance-cell">
            <div
              data-bs-toggle="tooltip"
              data-bs-title="Summation of all days in loss"
            >
              <label className="field-label">Overall Loss</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.OverallLoss}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div
              data-bs-toggle="tooltip"
              data-bs-title="Number of days in profit"
            >
              <label className="field-label">Profit Days</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.DaysProfit}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div>
              <label className="field-label">Risk to Reward Ratio</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.RiskToRewardRatio}
              </label>
            </div>
          </div>
        </div>
        <div className="overallperformance-row">
          <div className="overallperformance-cell">
            <div>
              <label className="field-label">Average Profit</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.AverageProfit}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div
              data-bs-toggle="tooltip"
              data-bs-title="Number of days in loss"
            >
              <label className="field-label">Loss Days</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.DaysLoss}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div>
              <label className="field-label">Max Drawdown</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.MaxDrawdown}
              </label>
            </div>
          </div>
        </div>
        <div className="overallperformance-row">
          <div className="overallperformance-cell">
            <div>
              <label className="field-label">Average Loss</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.AverageLoss}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div
              data-bs-toggle="tooltip"
              data-bs-title="Max (No of Consecutive  Days in Loss)"
            >
              <label className="field-label">Max Lossing Streak (trades)</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.MaxLosingStreak}
              </label>
            </div>
          </div>
          <div className="overallperformance-cell">
            <div>
              <label className="field-label">Expectancy Ratio</label>
            </div>
            <div>
              <label className="field-label">
                {overallPerformance.ExpectancyRatio}
              </label>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
