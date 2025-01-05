import { useEffect } from "react";
import { FullReport } from "../fullReport/FullReport";
import { OverallPerformance } from "../overallPerformance/OverallPerformance";
import "./BackTestReport.css";
import { formatDataForExcel, exportToExcel } from "../ExportToExcel";

export const BackTestReport = (props) => {
  const { data } = props;
  console.log("data", data);

  const download = () => {
    console.log("downloading...");
    const dataToExport = formatDataForExcel(data);
    console.log("dataToExport", dataToExport);
    exportToExcel({ data: dataToExport, fileName: "backtest_report" });
  };

  return (
    <>
      <div className="box">
        <div className="cell backtest-report-header">
          <h6 className="box-title">Backtest Report</h6>
          <button className="btn theme_button" onClick={download}>
            Export to Excel
          </button>
        </div>
        <div className="cell">
          <div className="box card">
            <table class="table table-responsive table-bordered table-striped table-hover">
              <thead>
                <tr>
                  <th scope="col">Year</th>
                  <th scope="col">Jan</th>
                  <th scope="col">Feb</th>
                  <th scope="col">Mar</th>
                  <th scope="col">Apr</th>
                  <th scope="col">May</th>
                  <th scope="col">Jun</th>
                  <th scope="col">Jul</th>
                  <th scope="col">Aug</th>
                  <th scope="col">Sep</th>
                  <th scope="col">Oct</th>
                  <th scope="col">Nov</th>
                  <th scope="col">Dec</th>
                  <th scope="col">Total</th>
                  <th scope="col">Max Drawdown</th>
                  <th scope="col" style={{ width: "120px" }}>
                    Days for MDD
                  </th>
                  <th scope="col">R/MDD (Yearly)</th>
                </tr>
              </thead>
              <tbody>
                {data &&
                  data.YearlyData &&
                  data.YearlyData.map((value) => {
                    return (
                      <tr>
                        <td>
                          <label className="field-label">{value.Year}</label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Jan
                              ? value.MonthlyPerformance.Jan
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Feb
                              ? value.MonthlyPerformance.Feb
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Mar
                              ? value.MonthlyPerformance.Mar
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Apr
                              ? value.MonthlyPerformance.Apr
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.May
                              ? value.MonthlyPerformance.May
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Jun
                              ? value.MonthlyPerformance.Jun
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Jul
                              ? value.MonthlyPerformance.Jul
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Aug
                              ? value.MonthlyPerformance.Aug
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Sep
                              ? value.MonthlyPerformance.Sep
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Oct
                              ? value.MonthlyPerformance.Oct
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Nov
                              ? value.MonthlyPerformance.Nov
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.MonthlyPerformance.Dec
                              ? value.MonthlyPerformance.Dec
                              : 0}
                          </label>
                        </td>
                        <td className="number">
                          <label className="field-label">
                            {value.Total ? value.Total : 0}
                          </label>
                        </td>
                        <td className="number-center">
                          <label className="field-label">
                            {value.MaxDrawdown ? value.MaxDrawdown : 0}
                          </label>
                        </td>
                        <td className="number-center">
                          <label className="field-label max-drawdown-label">
                            {value.DaysForMaxDrawdown
                              ? value.DaysForMaxDrawdown
                              : 0}
                          </label>
                          <br />
                          <label className="max-drawdown-duration">
                            {`[${value.DurationOfMaxDrawdown.start} to ${value.DurationOfMaxDrawdown.end}]`}
                          </label>
                        </td>
                        <td className="number-center">
                          <label className="field-label">
                            {value.ReturnToMaxDDYearly
                              ? value.ReturnToMaxDDYearly
                              : 0}
                          </label>
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div className="box">
        <div className="cell">
          <OverallPerformance overallPerformance={data.OverallPerformance} />
        </div>
      </div>
      <div className="box">
        <div className="cell">
          <FullReport tradebook={data.tradebook} />
        </div>
      </div>
    </>
  );
};
