const axios = require('axios');
const fs = require('fs');
const path = require('path');
const csvWriter = require('csv-writer').createObjectCsvWriter;

// Fetch master data
function getMasterData() {
    const exchanges = ["NSEFO", "BSEFO"];

    exchanges.forEach((ex) => {
        const url = "https://ttblaze.iifl.com/apimarketdata/instruments/master";
        const todayDate = new Date().toISOString().split('T')[0]; // Get today's date in 'YYYY-MM-DD' format
        const body = {
            exchangeSegmentList: [ex]
        };

        let csvFilename = '';
        if (ex === 'NSEFO') {
            csvFilename = `nfo.csv`;
        } else if (ex === 'BSEFO') {
            csvFilename = `bfo.csv`;
        }

        axios.post(url, body)
            .then((response) => {
                if (response.status === 200) {
                    const jsonData = response.data;

                    if (jsonData && jsonData.result) {
                        // Split the result string into individual lines
                        const lines = jsonData.result.split('\n');

                        // Prepare an array to hold the CSV data
                        const records = lines.map((line, index) => {
                            const fields = line.split('|');  // Split each line by '|'

                            return {
                                Index: index,
                                ExchangeSegment: fields[0] || '',
                                ExchangeInstrumentID: fields[1] || '',
                                InstrumentType: fields[2] || '',
                                Name: fields[3] || '',
                                Description: fields[4] || '',
                                Series: fields[5] || '',
                                NameWithSeries: fields[6] || '',
                                InstrumentID: fields[7] || '',
                                PriceBandHigh: fields[8] || '',    // Assuming field[8] corresponds to PriceBand.High
                                PriceBandLow: fields[9] || '',     // Assuming field[9] corresponds to PriceBand.Low
                                FreezeQty: fields[10] || '',
                                TickSize: fields[11] || '',        // Assuming field[11] corresponds to TickSize
                                LotSize: fields[12] || '',
                                Multiplier: fields[13] || '',      // Assuming field[13] corresponds to Multiplier
                                UnderlyingInstrumentId: fields[14] || '',
                                UnderlyingIndexName: fields[15] || '',
                                ContractExpiration: fields[16] || '',
                                StrikePrice: fields[17] || '',
                                OptionType: fields[18] || '',
                                DisplayName: fields[19] || '',     // Assuming field[19] corresponds to DisplayName
                                PriceNumerator: fields[20] || '',  // Assuming field[20] corresponds to PriceNumerator
                                PriceDenominator: fields[21] || '',// Assuming field[21] corresponds to PriceDenominator
                                DetailedDescription: fields[22] || ''  // Assuming field[22] corresponds to DetailedDescription
                            };
                        });

                        // Initialize CSV writer
                        const csvWriterInstance = csvWriter({
                            path: csvFilename,
                            header: [
                                { id: 'Index', title: '' },
                                { id: 'ExchangeSegment', title: 'ExchangeSegment' },
                                { id: 'ExchangeInstrumentID', title: 'ExchangeInstrumentID' },
                                { id: 'InstrumentType', title: 'InstrumentType' },
                                { id: 'Name', title: 'Name' },
                                { id: 'Description', title: 'Description' },
                                { id: 'Series', title: 'Series' },
                                { id: 'NameWithSeries', title: 'NameWithSeries' },
                                { id: 'InstrumentID', title: 'InstrumentID' },
                                { id: 'PriceBandHigh', title: 'PriceBand.High' },
                                { id: 'PriceBandLow', title: 'PriceBand.Low' },
                                { id: 'FreezeQty', title: 'FreezeQty' },
                                { id: 'TickSize', title: 'TickSize' },
                                { id: 'LotSize', title: 'LotSize' },
                                { id: 'Multiplier', title: 'Multiplier' },
                                { id: 'UnderlyingInstrumentId', title: 'UnderlyingInstrumentId' },
                                { id: 'UnderlyingIndexName', title: 'UnderlyingIndexName' },
                                { id: 'ContractExpiration', title: 'ContractExpiration' },
                                { id: 'StrikePrice', title: 'StrikePrice' },
                                { id: 'OptionType', title: 'OptionType' },
                                { id: 'DisplayName', title: 'DisplayName' },
                                { id: 'PriceNumerator', title: 'PriceNumerator' }
                            ]
                        });

                        // Write data to CSV file
                        csvWriterInstance.writeRecords(records)
                            .then(() => {
                                console.log(`Data written to ${csvFilename} successfully.`);
                            })
                            .catch((err) => {
                                console.error('Error writing to CSV file:', err);
                            });

                    } else {
                        console.error("Error: jsonData.result is missing or malformed.");
                    }
                } else {
                    console.error(`Error: Unable to fetch data (status code: ${response.status})`);
                }
            })
            .catch((err) => {
                console.error('Error during HTTP request:', err);
            });
    });
}

getMasterData();
