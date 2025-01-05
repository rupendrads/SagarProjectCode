const cluster = require('cluster');
const numCPUs = require('os').cpus().length;
const mysql = require('mysql');
const fs = require('fs');
const { spawn } = require('child_process');

// Define MySQL connection configuration
const dbConfig = {
    host: 'localhost',
    user: 'root',
    password: 'pegasus',
    database: 'index_data'
};
const startTime = new Date()
// Function to fetch futures data
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

// Promisified version of fs.readFile
function readFileAsync(file, encoding) {
    return new Promise((resolve, reject) => {
        fs.readFile(file, encoding, (err, data) => {
            if (err) reject(err);
            else resolve(data);
        });
    });
}
const maxThreads = 24;
if (cluster.isPrimary) {
    console.log(`Primary ${process.pid} is running`);

    // Run test.py script to generate JSON file
    const testProcess = spawn('python', ['test.py']);

    testProcess.on('exit', (code) => {
        if (code === 0) {
            console.log('test.py script execution completed successfully.');

            // Read JSON file after it's generated
            readFileAsync('nifty_2024-03-29.json', 'utf8')
                .then((data) => {
                    console.log('JSON file read successfully.');

                    // Fetch data once the JSON file is read
                    const startDate = '2021-01-01';
                    const endDate = '2021-05-30';
                    const instrument = 'NIFTY';
                    const type = 'I';

                    // Fetch futures data
                    fetchFuturesData(instrument, startDate, endDate, type)
                        .then((fetchedData) => {
                            console.log('Data fetched successfully.');

                            // Take only the first 10 combinations
                            const combinationData = JSON.parse(data).slice(0, 100);

                            let combinationsProcessed = 0; // Track the number of processed combinations
                            let threadsRunning = 0; // Track the number of running threads

                            // Function to fork a worker and handle 'thread_complete' event
                            function forkWorker() {
                                const combination = combinationData[combinationsProcessed++];
                                const worker = cluster.fork({ combinations: JSON.stringify([combination]), fetchedData: JSON.stringify(fetchedData) });
                                threadsRunning++;

                                worker.on('message', (msg) => {
                                    if (msg.type === 'thread_complete') {
                                        threadsRunning--;
                                        console.log(`Thread completed by Worker ${msg.workerPid}`);
                                        if (combinationsProcessed < combinationData.length && threadsRunning < maxThreads) {
                                            forkWorker(); // Fork a new worker if there are more combinations to process and thread limit is not reached
                                        } else if (threadsRunning === 0) {
                                            console.log('All threads completed.');
                                            const endTime = new Date();
                                            console.log(`Time taken ${endTime-startTime}`)
                                            
                                            process.exit(0);
                                        }
                                    }
                                });
                            }

                            // Fork workers up to the maximum thread limit
                            for (let i = 0; i < numCPUs && combinationsProcessed < combinationData.length && threadsRunning < maxThreads; i++) {
                                forkWorker();
                            }
                        })
                        .catch((error) => {
                            console.error('Error fetching data:', error);
                        });
                })
                .catch((error) => {
                    console.error('Error reading JSON file:', error);
                });
        } else {
            console.error('test.py script execution failed.');
        }
    });
} else {
    console.log(`Worker ${process.pid} started`);

    // Worker process logic
    const combinationData = JSON.parse(process.env.combinations);
    const fetchedData = JSON.parse(process.env.fetchedData);

    async function runTestScriptAndReadFile() {
        try {
            // Process combinations
            for (const combination of combinationData) {
                await spawnPythonProcess(combination, fetchedData);
            }
            // All threads have completed, signal the primary process
            process.send({ type: 'thread_complete', workerPid: process.pid });
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Start the worker process logic
    runTestScriptAndReadFile();
}

// Function to spawn Python process for a given combination
// Function to spawn Python process for a given combination
function spawnPythonProcess(combination, data) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', ['clone.py']);

        // Handle process error
        pythonProcess.on('error', (err) => {
            console.error(`Error spawning Python process: ${err}`);
            reject(err);
        });

        const inputData = JSON.stringify({ combination, data });
        pythonProcess.stdin.write(inputData);
        pythonProcess.stdin.end();

        const threadId = pythonProcess.pid; // Get the thread ID

        // Listen for process exit event
        pythonProcess.on('exit', (code) => {
            // console.log(`Thread ${threadId} exited with code ${code}`);
            resolve(); // Resolve the promise when the thread completes
        });
    });
}

