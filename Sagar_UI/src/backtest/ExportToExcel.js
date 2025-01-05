import { saveAs } from "file-saver";
import * as XLSX from "xlsx";

export const formatDataForExcel = (data) => {
  const tradebook = data.tradebook.map((trade) => {
    const entrydate = trade["entry_time"].split(" ")[0];
    const entrytime = trade["entry_time"].split(" ")[1];
    const exitdate = trade["exit_time"].split(" ")[0];
    const exittime = trade["exit_time"].split(" ")[1];
    let formattedTrade = {
      Symbol: trade.symbol,
      Trade: trade.trade,
      "Entry Date": entrydate,
      "Entry Time": entrytime,
      "Entry Price": trade.entry_price,
      "Exit Date": exitdate,
      "Exit Time": exittime,
      "Exit Price": trade.exit_price,
      SL: trade.sl,
      TSL: trade.tsl,
      Quantity: trade.qty,
      "P/L": trade.pnl,
      "Max Loss": trade.maxLossStrategy,
      "Max Profit": trade.maxProfitStrategy,
      "Future Entry": trade.futureEntry,
      "Future Exit": trade.futureExit,
      Comment: trade.comment,
    };
    delete formattedTrade.entry_time;
    delete formattedTrade.exit_time;
    return formattedTrade;
  });

  const yearlyData = data.YearlyData.map((yearlyData) => {
    const daysForMDD = `${yearlyData.DaysForMaxDrawdown}[${yearlyData.DurationOfMaxDrawdown.start} to ${yearlyData.DurationOfMaxDrawdown.end}]`;
    return {
      Year: yearlyData.Year,
      Jan: yearlyData.MonthlyPerformance.Jan,
      Feb: yearlyData.MonthlyPerformance.Feb,
      Mar: yearlyData.MonthlyPerformance.Mar,
      Apr: yearlyData.MonthlyPerformance.Apr,
      May: yearlyData.MonthlyPerformance.May,
      Jun: yearlyData.MonthlyPerformance.Jun,
      Jul: yearlyData.MonthlyPerformance.Jul,
      Aug: yearlyData.MonthlyPerformance.Aug,
      Sep: yearlyData.MonthlyPerformance.Sep,
      Oct: yearlyData.MonthlyPerformance.Oct,
      Nov: yearlyData.MonthlyPerformance.Nov,
      Dec: yearlyData.MonthlyPerformance.Dec,
      Total: yearlyData.Total,
      "Max Drawdown": yearlyData.MaxDrawdown,
      "Days for MDD": daysForMDD,
      "R/MDD (Yearly)": yearlyData.ReturnToMaxDDYearly,
    };
  });

  const overallPerformanceTitle = Object.freeze({
    TotalProfit: "Total Profit",
    NetProfit: "Net Profit",
    OverallProfit: "Overall Profit",
    OverallLoss: "Overall Loss",
    AverageProfit: "Average Profit",
    AverageLoss: "Average Loss",
    MaxProfitInSingleTrade: "Max Profit in Single Trade",
    MaxLossInSingleTrade: "Max Loss in Single Trade",
    TotalTradingDays: "Total Trading Days",
    DaysProfit: "Profit Days",
    DaysLoss: "Loss Days",
    MaxLosingStreak: "Max Losing Streak",
    MaxWinningStreak: "Max Winning Streak",
    MaxDDPeriod: "Max DD Period",
    DurationOfMaxDrawdown: "Duration at Max Drawdown",
    RiskToRewardRatio: "Risk to Reward Ratio",
    MaxDrawdown: "Max Drawdown",
    ExpectancyRatio: "Expectancy Ratio",
  });

  const overallPerformance = [];
  for (const opt in overallPerformanceTitle) {
    console.log("opt", opt);
    const title = overallPerformanceTitle[opt];
    let value = data.OverallPerformance[opt];
    if (opt === "DurationOfMaxDrawdown") {
      value = `${value.days} [${value.start} to ${value.end}]`;
    }
    overallPerformance.push({
      Title: title,
      Value: value,
    });
  }

  console.log("overallPerformance", overallPerformance);

  return {
    tradebook: tradebook,
    YearlyData: yearlyData,
    OverallPerformance: overallPerformance,
  };
};

export const exportToExcel = ({ data, fileName }) => {
  console.log("exportToExcel", data);
  const worksheetYearlyReport = XLSX.utils.json_to_sheet(data.YearlyData);
  const worksheetOverallPerformance = XLSX.utils.json_to_sheet(
    data.OverallPerformance
  );
  const worksheetFullReport = XLSX.utils.json_to_sheet(data.tradebook);

  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(
    workbook,
    worksheetYearlyReport,
    "Yearly Report"
  );
  XLSX.utils.book_append_sheet(
    workbook,
    worksheetOverallPerformance,
    "Overall Performance"
  );
  XLSX.utils.book_append_sheet(workbook, worksheetFullReport, "Full Report");
  const excelBuffer = XLSX.write(workbook, {
    bookType: "xlsx",
    type: "array",
  });
  const blob = new Blob([excelBuffer], { type: "application/octet-stream" });
  saveAs(blob, `${fileName}.xlsx`);
};
