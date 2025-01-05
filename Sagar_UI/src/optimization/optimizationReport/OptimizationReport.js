import { useState, useEffect, useRef } from "react";
import { Pagination } from "../../common/Pagination";
import appConfigData from "../../app-config.json";
import "./OptimizationReport.css";

const OptimizationReport = (props) => {
  const { data, dataLength, getTradeBookReport } = props;
  const [currentPageData, setCurrentPageData] = useState([]);
  const currentPageRef = useRef();

  console.log("processing optimization report data - ", data);

  useEffect(() => {
    pageChanged(0, appConfigData.OPTIMIZATION_REPORT_PAGE_LENGTH);
  }, []);

  useEffect(() => {
    if (currentPageRef && currentPageRef.current) {
      const currentPage = currentPageRef.current.getCurrentPage();
      const start =
        (currentPage - 1) * appConfigData.OPTIMIZATION_REPORT_PAGE_LENGTH;
      const end = start + appConfigData.OPTIMIZATION_REPORT_PAGE_LENGTH;
      pageChanged(start, end);
    }
  }, [data]);

  const pageChanged = (start, end) => {
    console.log("page changed");
    const pageData = data.slice(start, end);
    setCurrentPageData(pageData);
  };

  return (
    <>
      <div className="box">
        <div className="cell">
          <div className="box card table-responsive">
            <table class="table table-responsive table-bordered table-striped table-hover overflow-hidden">
              <thead>
                <tr>
                  <th scope="col">Combination Id</th>
                  <th scope="col">Net Profit</th>
                  <th scope="col">No. of Winning Trades</th>
                  <th scope="col">No. of Losing Trades</th>
                  <th scope="col">Winning Strike</th>
                  <th scope="col">Average profit/Trade</th>
                  <th scope="col">Average Loss/Trade</th>
                  <th scope="col">Days in Drawdown</th>
                  <th scope="col">System Drawdown</th>
                  <th scope="col">Max Drawdown</th>
                  <th scope="col"></th>
                  <th scope="col">Total Brokerage</th>
                  <th scope="col">Other Charges</th>
                  <th scope="col">Funds Required</th>
                  <th scope="col">Exposure</th>
                  <th scope="col">CAGR</th>
                </tr>
              </thead>
              <tbody>
                {currentPageData && currentPageData.length === 0 && (
                  <tr>
                    <td colspan="16" style={{ paddingLeft: "400px" }}>
                      <h6>Optimization pending...</h6>
                    </td>
                  </tr>
                )}
                {currentPageData &&
                  currentPageData.map((row) => {
                    const value = row.response.OverallPerformance;
                    return (
                      <tr>
                        <td>
                          <label className="field-label">
                            {row.sequence_id}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.NetProfit}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.DaysProfit}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.DaysLoss}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.DaysProfit / value.DaysLoss}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.AverageProfit}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.AverageLoss}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.DurationOfMaxDrawdown.days
                              ? value.DurationOfMaxDrawdown.days
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MaxDrawdown}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MaxDrawdown}
                          </label>
                        </td>
                        <td>
                          <button
                            className="btn btn-light optimization-tradbook-button"
                            type="button"
                            onClick={() => getTradeBookReport(row.sequence_id)}
                          >
                            Trade Book
                          </button>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.TaxAndCharges.Brokerage
                              ? value.TaxAndCharges.Brokerage
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.TaxAndCharges.OtherCharges
                              ? value.TaxAndCharges.OtherCharges
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.FundsRequired}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.Exposure}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">{value.Cagr}</label>
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
          <Pagination
            postsPerPage={appConfigData.OPTIMIZATION_REPORT_PAGE_LENGTH}
            length={dataLength}
            pageChanged={pageChanged}
            _refCurrentPage={currentPageRef}
          />
        </div>
      </div>
    </>
  );
};

export default OptimizationReport;
