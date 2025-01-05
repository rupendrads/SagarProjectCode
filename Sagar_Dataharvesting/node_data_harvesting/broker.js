var XtsMarketDataAPI = require('xts-marketdata-api').XtsMarketDataAPI;
const fs = require('fs');

const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));

async function login() {
  try {
    const environment = config.environment;
    let secretKey, appKey, url;

    if (environment === 'live') {
      secretKey = config.liveSecretKey;
      appKey = config.liveAppKey;
      url = config.liveURL;
    } else {
      secretKey = config.sandboxSecretKey;
      appKey = config.sandboxAppKey;
      url = config.sandboxURL;
    }

    const xtsMarketDataAPI = new XtsMarketDataAPI(url);

    const loginRequest = {
      secretKey: secretKey,
      appKey: appKey,
    };
    console.log(loginRequest)
    let logInResponse = await xtsMarketDataAPI.logIn(loginRequest);

    return { xtsMarketDataAPI, logInResponse };
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

module.exports = { login };
