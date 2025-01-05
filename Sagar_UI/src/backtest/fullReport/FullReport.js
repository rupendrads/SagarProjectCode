import { useEffect, useState } from "react";
import "./FullReport.css";
import { Pagination } from "../../common/Pagination";

export const FullReport = (props) => {
  console.log("props", props);
  const { tradebook } = props;

  console.log("tradebook", tradebook);
  const [currentPageTrades, setCurrentPageTrades] = useState([]);

  useEffect(() => {
    pageChanged(0, 8);
  }, []);

  const pageChanged = (start, end) => {
    console.log(tradebook.length);
    console.log("start", start);
    console.log("end", end);
    const pageTrades = tradebook.slice(start, end);
    setCurrentPageTrades(pageTrades);
  };

  return (
    <div>
      <div className="cell overallperformance-header">
        <h6 className="box-title">Full Report</h6>
      </div>
      <div className="box card table-responsive">
        <table class="table table-responsive table-bordered table-striped table-hover full-report-table overflow-hidden">
          <thead>
            <tr>
              <th scope="col">Symbol</th>
              <th scope="col">Trade</th>
              <th scope="col">Entry Date</th>
              <th scope="col">Entry Time</th>
              <th scope="col">Entry Price</th>
              <th scope="col">Exit Date</th>
              <th scope="col">Exit Time</th>
              <th scope="col">Exit Price</th>
              <th scope="col">SL</th>
              <th scope="col">TSL</th>
              <th scope="col">Quantity</th>
              <th scope="col">P/L</th>
              <th scope="col">Max Loss</th>
              <th scope="col">Max Profit</th>
              <th scope="col">Future Entry</th>
              <th scope="col">Future Exit</th>
              <th scope="col">Comment</th>
            </tr>
          </thead>
          <tbody>
            {currentPageTrades &&
              currentPageTrades.map((value) => {
                return (
                  <tr>
                    <td>
                      <label className="field-label">{value.symbol}</label>
                    </td>
                    <td className="fullReport-bs">
                      <label className="field-label">{value.trade}</label>
                    </td>
                    <td className="fullReport-date">
                      <label className="field-label">
                        {value.entry_time.split(" ")[0]}
                      </label>
                    </td>
                    <td className="fullReport-time">
                      <label className="field-label">
                        {value.entry_time.split(" ")[1]}
                      </label>
                    </td>
                    <td className="number">
                      <label className="field-label">{value.entry_price}</label>
                    </td>
                    <td className="fullReport-date">
                      <label className="field-label">
                        {value.exit_time.split(" ")[0]}
                      </label>
                    </td>
                    <td className="fullReport-time">
                      <label className="field-label">
                        {value.exit_time.split(" ")[1]}
                      </label>
                    </td>
                    <td className="number">
                      <label className="field-label">{value.exit_price}</label>
                    </td>
                    <td className="number">
                      <label className="field-label">{value.sl}</label>
                    </td>
                    <td className="number">
                      <label className="field-label">{value.tsl}</label>
                    </td>
                    <td className="number">
                      <label className="field-label">{value.qty}</label>
                    </td>
                    <td className="number">
                      <label className="field-label">{value.pnl}</label>
                    </td>
                    <td className="number">
                      <label className="field-label">
                        {value.maxLossStrategy}
                      </label>
                    </td>
                    <td className="number">
                      <label className="field-label">
                        {value.maxProfitStrategy}
                      </label>
                    </td>
                    <td className="number">
                      <label className="field-label">{value.futureEntry}</label>
                    </td>
                    <td className="number">
                      <label className="field-label">{value.futureExit}</label>
                    </td>
                    <td>
                      <label className="field-label">{value.comment}</label>
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
        <Pagination
          postsPerPage={8}
          length={tradebook.length}
          pageChanged={pageChanged}
        />
      </div>
    </div>
  );
};
