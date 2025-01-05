const XtsMarketDataWS = require('xts-marketdata-api').WS;
const { login } = require('./broker');
const config = require('./config.json');
const MDEmitter = require('./MDSocket');  // Corrected the path to MDsocket.js
var settings = require('./config/settings.json');  // Updated path

async function main() {
  try {
    const { xtsMarketDataAPI, logInResponse } = await login();
    console.log(logInResponse);
    
    const url = config.environment === 'live' ? config.liveURL : config.sandboxURL;

    // Instantiate the MDEmitter class
    const xtsMarketDataWS = new MDEmitter(url);
    
    const socketInitRequest = {
      userID: 'PEGASUSC',
      publishFormat: 'JSON',
      broadcastMode: 'Full',
      token: logInResponse.result.token, 
    };

    // Initialize the socket connection
    xtsMarketDataWS.init(socketInitRequest);

    // Register event listeners
    registerEvents(xtsMarketDataAPI, xtsMarketDataWS);

    let response = await xtsMarketDataAPI.clientConfig();
    console.log("Response from initialization: " + response);
  } catch (error) {
    console.error('An error occurred:', error);
  }
}

function registerEvents(xtsMarketDataAPI, xtsMarketDataWS) {
  xtsMarketDataWS.eventEmitter.on('connect', (connectData) => {
    console.log("Connected: " + connectData);
    subscribeToMarketData(xtsMarketDataAPI, xtsMarketDataWS);
  });

  xtsMarketDataWS.eventEmitter.on('joined', (joinedData) => {
    console.log("Joined: " + joinedData);
  });

  xtsMarketDataWS.eventEmitter.on('1512-json-full', (marketDepthData) => {
    console.log("Market Depth Event (1512-json-full): ", marketDepthData);
  });

  xtsMarketDataWS.eventEmitter.on('candleData', (candleData) => { 
    console.log("Candle Data: " + candleData);
  });

  xtsMarketDataWS.eventEmitter.on('logout', (logoutData) => {
    console.log("Logout: " + logoutData);
  });
}

async function subscribeToMarketData(xtsMarketDataAPI, xtsMarketDataWS) {
  try {
    let subscriptionRequest = {
      instruments: [
        {
          exchangeSegment: xtsMarketDataAPI.exchangeSegments.NSECM,
          exchangeInstrumentID: 26000,
        },
      ],
      xtsMessageCode: 1512,
    };

    let response = await xtsMarketDataAPI.subscription(subscriptionRequest);
    console.log('Subscription response:', response);
  } catch (error) {
    console.error('Subscription error:', error);
  }
}

main();
