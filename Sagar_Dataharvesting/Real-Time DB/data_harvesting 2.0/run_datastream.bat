@echo on


:: Change to D drive
D:

cd "D:\Rupendra\Work\Sagar\Sagar_Dataharvesting\Real-Time DB\data_harvesting 2.0"

python datastream.py

: Check if the previous command (node redis.js) was successful
if %errorlevel% neq 0 (
    echo An error occurred while running datastream.js..
) else (
    echo datastream.js executed successfully.
)

:: Pause to keep the window open for debugging (optional)
pause