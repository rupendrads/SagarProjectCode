const axios = require("axios");
const fs = require("fs");
const path = require("path");
const { parse } = require("csv-parse/sync");

class XTS {
  constructor() {
    this.marketUrl = "https://ttblaze.iifl.com/apimarketdata/auth/login";
    this.masterInstrumentsUrl = "https://ttblaze.iifl.com/apimarketdata/instruments/master";
    this.subscriptionUrl = "https://ttblaze.iifl.com/apimarketdata/instruments/subscription"
    this.headers = { "Content-Type": "application/json" };
    this.xtsSubscribedSymbols = [];
    this.tokenFilePath = path.join(__dirname, "xts_tokens.json");
    this.nfoCsvPath = path.join(__dirname, "nfo.csv");

    const tokens = this.loadTokensFromFile();
    if (tokens && tokens.date === new Date().toISOString().split("T")[0]) {
      this.marketToken = tokens.marketToken;
      this.interactiveToken = tokens.interactiveToken;
      this.userid = tokens.userID;
      console.log("Tokens loaded from xts_tokens.json");
    }
  }

  // Save tokens to a JSON file
  saveTokensToFile(tokens) {
    try {
      fs.writeFileSync(this.tokenFilePath, JSON.stringify(tokens, null, 2), "utf-8");
      console.log("Tokens saved to xts_tokens.json");
    } catch (error) {
      console.error("Failed to save tokens:", error.message);
    }
  }

  // Load tokens from JSON file
  loadTokensFromFile() {
    try {
      if (fs.existsSync(this.tokenFilePath)) {
        const tokens = JSON.parse(fs.readFileSync(this.tokenFilePath, "utf-8"));
        console.log("Tokens loaded from xts_tokens.json");
        return tokens;
      }
    } catch (error) {
      console.error("Failed to load tokens:", error.message);
    }
    return null;
  }
  async getQuotes(instruments) {
    const headers = { ...this.headers, Authorization: this.marketToken };
    const payload = {
      instruments: instruments,
      xtsMessageCode: 1512,
      publishFormat: "JSON",
    };
  
    try {
      const response = await axios.post(
        "https://ttblaze.iifl.com/marketdata/instruments/quotes",
        payload,
        { headers }
      );
  
      // Log and return the response data
      console.log("Quotes Response Data:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error fetching quotes:", error.message);
      if (error.response) {
        // Log additional error details if available
        console.error("Error Response Data:", error.response.data);
        console.error("Error Response Status:", error.response.status);
        console.error("Error Response Headers:", error.response.headers);
      }
      return null;
    }
  }
  
  // Market login
  async marketLogin(secretKey, appKey) {
    try {
      const response = await axios.post(this.marketUrl, {
        secretKey,
        appKey,
        source: "WebAPI",
      });
      const data = response.data;
      if (data.type === "success") {
        this.marketToken = data.result.token;
        this.userid = data.result.userID;
        console.log("Market login successful");
        this.saveTokensToFile({
          marketToken: this.marketToken,
          interactiveToken: this.interactiveToken,
          userID: this.userid,
          date: new Date().toISOString().split("T")[0],
        });
        return { token: this.marketToken, userID: this.userid };
      } else {
        console.error("Market login failed:", data.message);
        return null;
      }
    } catch (error) {
      console.error("Market login error:", error.response?.data || error.message);
      return null;
    }
  }

  // Fetch master instruments and save to nfo.csv
  

  // Parse instrument data using csv-parse/sync
  
  async subscribeSymbols(instruments) {
    try {
      const newInstruments = instruments.filter(
        (instrument) => !this.xtsSubscribedSymbols.includes(instrument)
      );
      if (newInstruments.length > 0) {
        const response = await axios.post(
          this.subscriptionUrl,
          {
            instruments: newInstruments,
            xtsMessageCode: 1512,
          },
          { headers: { Authorization: this.marketToken } }
        );
  
        // Log the entire response
        // console.log("Response:", response);
  
        // Log specific parts of the response
        console.log("Response Data:", response.data);
        // console.log("Response Status:", response.status);
        // console.log("Response Headers:", response.headers);
  
        this.xtsSubscribedSymbols.push(...newInstruments);
        // console.log(this.xtsSubscribedSymbols);
        // console.log("Subscribed to new instruments.");
      } else {
        console.log("No new instruments to subscribe.");
      }
    } catch (error) {
      console.error("Failed to subscribe symbols:", error.message);
      if (error.response) {
        // Log error response details if available
        console.error("Error Response Data:", error.response.data);
        console.error("Error Response Status:", error.response.status);
        console.error("Error Response Headers:", error.response.headers);
      }
    }
  }
  
  // Save parsed data to a CSV file
  saveToCsv(data, filePath) {
    try {
      const headers = Object.keys(data[0]).join(",");
      const csvContent = [headers, ...data.map((row) => Object.values(row).join(","))].join("\n");
      fs.writeFileSync(filePath, csvContent, "utf-8");
      console.log(`Data successfully saved to ${filePath}`);
    } catch (error) {
      console.error("Error saving data to CSV:", error.message);
    }
  }
}

module.exports = XTS;




