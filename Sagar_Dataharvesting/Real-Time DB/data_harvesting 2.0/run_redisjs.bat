@echo on

:: Change to D drive
D:

:: Change directory to your desired folder on D drive
cd "D:\Rupendra\Work\Sagar\Sagar_Dataharvesting\Real-Time DB\data_harvesting 2.0"


:: Wait for 10 seconds before running the script
timeout /t 10 /nobreak

:: Run your Node.js script and log the output
node redis.js

:: Check if the previous command (node redis.js) was successful
if %errorlevel% neq 0 (
    echo An error occurred while running redis.js. Check node_script_log.txt for details.
) else (
    echo redis.js executed successfully.
)

:: Pause to keep the window open for debugging (optional)
pause
