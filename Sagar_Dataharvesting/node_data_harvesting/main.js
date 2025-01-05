const XtsMarketDataWS = require('xts-marketdata-api').WS;
const { login } = require('./broker');
const config = require('./config.json');

async function main() {
  try {
    const { xtsMarketDataAPI, logInResponse } = await login();
    console.log(logInResponse)
    const url = config.environment === 'live' ? config.liveURL : config.sandboxURL;

    const xtsMarketDataWS = new XtsMarketDataWS(url);
    
    var socketInitRequest = {
      userID: 'PEGASUSC',
      publishFormat: 'JSON',
      broadcastMode: 'Full',
      token: logInResponse.result.token, 
    };

    xtsMarketDataWS.init(socketInitRequest);
    registerEvents(xtsMarketDataAPI, xtsMarketDataWS);

    let response = await xtsMarketDataAPI.clientConfig();
    console.log("response coming from initialization" + response);
  } catch (error) {
    console.error('An error occurred:', error);
  }

}
  


function registerEvents(xtsMarketDataAPI, xtsMarketDataWS) {
  xtsMarketDataWS.onConnect((connectData) => {
    console.log("onconnect" + connectData);
    subscribeToMarketData(xtsMarketDataAPI, xtsMarketDataWS);
  });

  xtsMarketDataWS.onJoined((joinedData) => {
    console.log(joinedData);
  });



  xtsMarketDataWS.onMarketDepth100Event((marketDepth100Data) => {
    console.log(marketDepth100Data);
  });

  // xtsMarketDataWS.onInstrumentPropertyChangeEvent((propertyChangeData) => {
  //   console.log(propertyChangeData);
  // });

  xtsMarketDataWS.onCandleDataEvent((candleData) => {
    console.log(candleData);
  });

  xtsMarketDataWS.onLogout((logoutData) => {
    console.log(logoutData);
  });
}

async function subscribeToMarketData(xtsMarketDataAPI, xtsMarketDataWS) {
  try {
    let subscriptionRequest = {
      instruments: [
        {
          exchangeSegment: xtsMarketDataAPI.exchangeSegments.NSEFO,
          exchangeInstrumentID: 35415,
        },
        {
          exchangeSegment: xtsMarketDataAPI.exchangeSegments.NSEFO,
          exchangeInstrumentID: 35089,
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
