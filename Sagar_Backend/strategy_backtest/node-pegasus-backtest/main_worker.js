const { Worker, workerData } = require('worker_threads');
const fs = require('fs');
const { performance } = require('perf_hooks');
const mysql = require('mysql');
const { spawn } = require('child_process');
const dbConfig = {
    host: 'localhost',
    user: 'root',
    password: 'pegasus',
    database: 'index_data'
};

function fetchFuturesData(instrument, startDate, endDate, type) {
    return new Promise((resolve, reject) => {
        // Create MySQL connection
        const connection = mysql.createConnection(dbConfig);

        // Define SQL query
        const futuresTable = `${instrument}_fut`;
        let query = `
            SELECT * FROM ${futuresTable} 
            WHERE DATE(timestamp) BETWEEN '${startDate}' AND '${endDate}' 
            AND expiry = '${type}'
        `;

        // Execute SQL query
        connection.query(query, (error, results, fields) => {
            if (error) {
                reject(error);
            } else {
                // Close MySQL connection
                connection.end();

                // Resolve with fetched data
                resolve(results);
            }
        });
    });
}

// Define function to read JSON file
function readJSONFile(file) {
    return new Promise((resolve, reject) => {
        fs.readFile(file, 'utf8', (err, data) => {
            if (err) {
                reject(err);
            } else {
                resolve(data);
            }
        });
    });
}

// Define function to chunkify an array
function chunkify(array, n) {
    let chunks = [];
    for (let i = 0; i < array.length; i += n) {
        chunks.push(array.slice(i, i + n));
    }
    return chunks;
}

// Define function to run test.py
function runTestScript() {
    return new Promise((resolve, reject) => {
        const { spawn } = require('child_process');
        const testProcess = spawn('python', ['test.py']);

        testProcess.stdout.on('data', (data) => {
            console.log(`Test.py stdout: ${data}`);
        });

        testProcess.stderr.on('data', (data) => {
            console.error(`Test.py stderr: ${data}`);
        });

        testProcess.on('exit', (code) => {
            console.log('Test.py finished');
            resolve();
        });

        testProcess.on('error', (err) => {
            console.error('Error running test.py:', err);
            reject(err);
        });
    });
}

// Define function to spawn workers and process combinations
// async function run() {
//     const total_time =0
//     const tick = performance.now();
//     const startDate = '2021-01-01';
//     const endDate = '2021-05-30';
//     const instrument = 'NIFTY';
//     const type = 'I';
//     const fetchedData = await fetchFuturesData(instrument, startDate, endDate, type);
//     // Run test.py script to generate data
//     // console.log('Running test.py script...');
//     // await runTestScript();

//     // Read JSON file after it's generated
//     console.log('Reading JSON file...');
//     const jsonData = await readJSONFile('nifty_2024-04-04.json');
//     const combinationData = JSON.parse(jsonData).slice(0, 100); // Take only the first 10000 combinations
//     console.log(combinationData)
//     // Define number of workers and maximum concurrent threads
//     const numWorkers = 4;
//     const maxConcurrentThreads = 6;
//     const workersCompleted = 0
//     // Chunkify the combination data for each worker
//     const chunks = chunkify(combinationData, Math.ceil(combinationData.length / numWorkers));
//     chunks.forEach((data) => {
//         const worker = new Worker('./workerInstance.js');
//         worker.postMessage({ combinations: data, fetchedData: fetchedData });
//         worker.on('message', () => {

//             console.log(`worker finished`);
//         });
    
//     });
    
   
// }

// // Start the process
// run();
function runTestScript() {
    return new Promise((resolve, reject) => {
        const testProcess = spawn('python', ['test.py']);

        testProcess.stdout.on('data', (data) => {
            // console.log(`Test.py stdout: ${data}`);
        });

        testProcess.stderr.on('data', (data) => {
            console.error(`Test.py stderr: ${data}`);
        });

        testProcess.on('exit', (code) => {
            // console.log('Test.py finished');
            resolve();
        });

        testProcess.on('error', (err) => {
            console.error('Error running test.py:', err);
            reject(err);
        });
    });
}
async function run() {
    const startDate = '2021-01-01';
    const endDate = '2021-05-30';
    const instrument = 'NIFTY';
    const type = 'I';
    console.log('running test script')
    await runTestScript()
    console.log('done')
    const fetchedData = await fetchFuturesData(instrument, startDate, endDate, type);
    
    console.log('Reading JSON file...');
    const jsonData = await readJSONFile('nifty_2024-04-05.json');
    const combinationData = JSON.parse(jsonData).slice(0, 100); 
    const tick = performance.now();

    const numWorkers = 1;
    const maxConcurrentThreads = 6;
    let workersCompleted = 0; 

    const chunks = chunkify(combinationData, Math.ceil(combinationData.length / numWorkers));
    console.log(chunks)
    chunks.forEach((data) => {
        const worker = new Worker('./workerInstance.js');
        worker.postMessage({ combinations: data, fetchedData: fetchedData });
        worker.on('message', () => {
            workersCompleted++;
            console.log(`worker${workersCompleted} finished`)
            if (workersCompleted === numWorkers) {
                const totalTime = performance.now() - tick;
                console.log(`All workers finished in ${totalTime} ms`);
                process.exit(0);
            }
        });
    });
}
run()