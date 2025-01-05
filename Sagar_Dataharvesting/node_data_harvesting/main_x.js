const XtsMarketDataWS = require('xts-marketdata-api').WS;
const { login } = require('./broker');
const { createDatabaseAndTable, insertDataIntoTable } = require('./utils');
const config = require('./config.json');
const moment = require('moment');

async function main() {
  try {
    const { xtsMarketDataAPI, logInResponse } = await login();

    const url = config.environment === 'live' ? config.liveURL : config.sandboxURL;

    const xtsMarketDataWS = new XtsMarketDataWS(url);

    var socketInitRequest = {
      userID: 'IIFL11',
      publishFormat: 'JSON',
      broadcastMode: 'Full',
      token: logInResponse.result.token,
    };

    xtsMarketDataWS.init(socketInitRequest);
    registerEvents(xtsMarketDataAPI, xtsMarketDataWS);

    let response = await xtsMarketDataAPI.clientConfig();
    console.log("response coming from initialization", response); // Corrected logging

    // Initialize database and table if not exists
    await createDatabaseAndTable();

    let counter = 0;
    let dataAccumulator = [];

    xtsMarketDataWS.addListener('1512-json-partial', (data) => {
      dataAccumulator.push(data);
      counter++;

      if (counter === 1500) {
        insertDataIntoTable(dataAccumulator)
          .then(() => {
            console.log('Data inserted into database.');
          })
          .catch((error) => {
            console.error('Error inserting data into database:', error);
          });

        counter = 0;
        dataAccumulator = [];
      }
    });

  } catch (error) {
    console.error('An error occurred:', error);
  }
}

function registerEvents(xtsMarketDataAPI, xtsMarketDataWS) {

  xtsMarketDataWS.onConnect((connectData) => {
    console.log('Socket connected successfully:', connectData);
    subscribeToMarketData(xtsMarketDataAPI, xtsMarketDataWS);
  });

  xtsMarketDataWS.onJoined((joinedData) => {
    console.log('Socket joined successfully:', joinedData);
  });

  xtsMarketDataWS.onError((errorData) => {
    console.error('Socket error:', errorData);
  });

  xtsMarketDataWS.onDisconnect((disconnectData) => {
    console.log('Socket disconnected:', disconnectData);
  });

  xtsMarketDataWS.onLogout((logoutData) => {
    console.log('Socket logged out:', logoutData);
  });
}

async function subscribeToMarketData(xtsMarketDataAPI, xtsMarketDataWS) {
  try {
    let subscriptionRequest = {
      instruments: [
        {
          exchangeSegment: xtsMarketDataAPI.exchangeSegments.NSECM,
          exchangeInstrumentID: 22,
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
