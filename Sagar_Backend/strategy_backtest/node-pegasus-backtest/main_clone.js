const { spawn } = require('child_process');
const mysql = require('mysql');
const fs = require('fs');

// Define MySQL connection configuration
const dbConfig = {
    host: 'localhost',
    user: 'root',
    password: 'pegasus',
    database: 'index_data'
};

// Define function to fetch futures data
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

// Function to spawn Python process for a given combination
function spawnPythonProcess(combination, data) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', ['clone.py']);

        // Pass combination and data as standard input to Python script
        const inputData = JSON.stringify({ combination, data });
        pythonProcess.stdin.write(inputData);
        pythonProcess.stdin.end();

        const threadId = pythonProcess.pid; // Get the thread ID

        // Listen for process stdout event
        pythonProcess.stdout.on('data', (data) => {
            console.log(`Thread ${threadId} stdout: ${data}`);
            const performance = data
            // console.log(`Rupendra ${performance}`);
        });

        // Listen for process stderr event
        pythonProcess.stderr.on('data', (data) => {
            console.error(`Thread ${threadId} stderr: ${data}`);
        });

        // Listen for process exit event
        pythonProcess.on('exit', (code) => {
            // Resolve the promise when the thread completes
            // console.log(`Thread ${threadId} exited`);
            resolve(threadId); // Pass thread ID when resolving
        });

        // Listen for process error event
        pythonProcess.on('error', (err) => {
            // Reject the promise if there's an error
            console.error(`Error spawning Python process for thread ${threadId}: ${err}`);
            reject(err);
        });
    });
}

async function runTestScriptAndReadFile() {
    const startTime = Date.now();
    try {
        const startDate = '2021-01-01';
        const endDate = '2021-05-30';
        const instrument = 'NIFTY';
        const type = 'I';
        console.log('running test script')
        await runTestScript();
        console.log('Test.py executed successfully.');
        
        // Read JSON file
        const data = await readFileAsync('nifty_2024-03-29.json', 'utf8');
        console.log('JSON file read successfully.');

        // Proceed to fetch data and launch threads
        const allCombinations = JSON.parse(data).slice(0, 1000); // Take only the first 100 combinations
        console.log('All combinations read from file:');

        // Fetch futures data

        const fetchedData = await fetchFuturesData(instrument, startDate, endDate, type);
        console.log('Data fetched successfully.');

        const maxConcurrentThreads = 15;
        let activeThreads = 0;
        let index = 0;

        // Function to launch new threads
        async function launchThreads() {
            while (index < allCombinations.length && activeThreads < maxConcurrentThreads) {
                const combination = allCombinations[index++];
                // console.log(`Thread ${index} started `)
                activeThreads++;
                spawnPythonProcess(combination, fetchedData)
                    .then(() => {
                        activeThreads--;
                        // Launch new threads recursively
                        launchThreads();
                    })
                    .catch((err) => {
                        console.error('Thread terminated due to error spawning Python process:', err);
                        activeThreads--;
                        // Launch new threads recursively
                        launchThreads();
                    });
            }
        }

        // Launch initial batch of threads
        launchThreads();
        const endTime = Date.now();
        const timeTaken = endTime - startTime;
        console.log(`Total time taken: ${timeTaken} milliseconds`);
    } catch (error) {
        console.error('Error:', error);
    }

}

// Function to run test.py
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

// Promisified version of fs.readFile
function readFileAsync(file, encoding) {
    return new Promise((resolve, reject) => {
        fs.readFile(file, encoding, (err, data) => {
            if (err) reject(err);
            else resolve(data);
        });
    });
}
// Start the process
runTestScriptAndReadFile();
