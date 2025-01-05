const { parentPort, workerData } = require('worker_threads');
const { spawn } = require('child_process');

// Function to process combinations
async function processCombinations(combinations, fetchedData) {
    // Semaphore to control the number of active threads
    let activeThreads = 0;
    let maxThreads = 5
    // Helper function to spawn a Python process for a combination
    function spawnPythonProcess(combination) {
        const pythonProcess = spawn('python', ['clone.py']);
        const inputData = JSON.stringify({ combination, fetchedData });
        pythonProcess.stdin.write(inputData);
        pythonProcess.stdin.end();

        pythonProcess.stdout.on('data', (data) => {
            // console.log(`Combination stdout: ${data}`);
        });

        pythonProcess.stderr.on('data', (data) => {
            // console.error(`Combination ${combination} stderr: ${data}`);
        });

        pythonProcess.on('exit', (code) => {
            // When a thread completes, decrement the activeThreads count
            activeThreads--;

            // If there are more combinations to process, spawn a new thread
            if (combinations.length > 0) {
                spawnNextThread();
            } else if (activeThreads === 0) {
                // If no active threads left and no more combinations, signal completion
                parentPort.postMessage('Worker completed processing');
            }
        });
    }

    // Function to spawn the next thread
    function spawnNextThread() {
        if (activeThreads < maxThreads && combinations.length > 0) {
            const combination = combinations.shift(); // Remove the first combination
            spawnPythonProcess(combination);
            activeThreads++;
        }
    }

    // Initial spawn of threads
    for (let i = 0; i < maxThreads; i++) {
        spawnNextThread();
    }
}

// Listen for messages from the parent thread
parentPort.on('message', ({ combinations, fetchedData }) => {
    // Process combinations
    processCombinations(combinations, fetchedData);
});
