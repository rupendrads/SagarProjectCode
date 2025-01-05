const fs = require("fs");
const path = require("path");
const moment = require("moment");

function brokerLogin(tokensFile = "xts_tokens.json") {
  const filePath = path.resolve(tokensFile);
  if (fs.existsSync(filePath)) {
    const data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    const lastDate = moment(data.date, "YYYY-MM-DD");

    if (lastDate.isSame(moment(), "day")) {
      console.log(data)
      return {
        marketToken: data.marketToken,

        userID: data.userID,
      };
    }
  }
  return null; // Tokens missing or outdated
}


module.exports = { brokerLogin };
