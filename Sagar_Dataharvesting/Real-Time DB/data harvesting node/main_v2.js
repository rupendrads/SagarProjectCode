const XTS = require("./broker");
const { brokerLogin } = require("./datastream");
const MDSocket = require("./marketsocketstream");
const { creds, range_percentage } = require("./constants");
const fs = require("fs");
const Redis = require('ioredis');
const { DateTime } = require('luxon'); // For date handling

(async () => {
    // Initialize Redis client
    const redis = new Redis({
        host: 'localhost',
        port: 6379,
        // Add other Redis configuration options if necessary
    });

    // Name of the JSON file to store the date and redis_flush flag
    const dataEraserFile = 'data_eraser.json'; // You can rename this if you have a better name

    // Function to flush Redis
    const flushRedis = async () => {
        await redis.flushall();
        console.log('Redis flushed successfully.');
    };

    // Get current date in 'YYYY-MM-DD' format
    const currentDate = DateTime.now().toISODate();

    if (fs.existsSync(dataEraserFile)) {
        // File exists
        try {
            const data = fs.readFileSync(dataEraserFile, 'utf8');
            const json = JSON.parse(data);

            if (json.date === currentDate) {
                // Same date
                if (!json.redis_flush) {
                    // redis_flush is false, so flush Redis and set redis_flush to true
                    await flushRedis();
                    json.redis_flush = true;

                    fs.writeFileSync(dataEraserFile, JSON.stringify(json));
                    console.log('Updated data_eraser.json with redis_flush set to true.');
                } else {
                    // redis_flush is true, do nothing
                    console.log('Redis already flushed for today.');
                }
            } else {
                // Different date
                // Update date, flush Redis, set redis_flush to true
                await flushRedis();
                json.date = currentDate;
                json.redis_flush = true;

                fs.writeFileSync(dataEraserFile, JSON.stringify(json));
                console.log('Updated data_eraser.json with new date and redis_flush set to true.');
            }
        } catch (err) {
            console.error('Error reading or parsing data_eraser.json:', err.message);
            // Handle error, possibly flush Redis and recreate data_eraser.json
            await flushRedis();
            const json = {
                date: currentDate,
                redis_flush: true
            };
            fs.writeFileSync(dataEraserFile, JSON.stringify(json));
            console.log('Recreated data_eraser.json with current date and redis_flush set to true.');
        }
    } else {
        // File does not exist
        // Flush Redis and create data_eraser.json with current date and redis_flush set to true
        await flushRedis();
        const json = {
            date: currentDate,
            redis_flush: true
        };
        fs.writeFileSync(dataEraserFile, JSON.stringify(json));
        console.log('Created data_eraser.json with current date and redis_flush set to true.');
    }

    // Proceed with the rest of your code

    const xts = new XTS();

    if (!xts.marketToken || !xts.interactiveToken) {
        const marketLoginResponse = await xts.marketLogin(
            creds.market_secret,
            creds.market_key
        );
        if (!marketLoginResponse) {
            console.error("Market login failed. Please check your credentials.");
            return;
        }
    }

    const mdSocket = new MDSocket(
        xts.marketToken,
        xts.userid,
        creds.port
    );
    mdSocket.connect();

    let instruments = [];
    try {
        const data = fs.readFileSync("subscription_list.json", "utf8");
        instruments = JSON.parse(data);
        console.log(instruments)
    } catch (err) {
        console.error("Error reading subscription_list.json:", err.message);
        return;
    }

    await xts.subscribeSymbols(instruments);
    // console.log("Market data socket connected.");
})();
