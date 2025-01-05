import time
import subprocess
import json
import logging

# Configure logging
logging.basicConfig(filename='scheduler.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_start_time():
 
    with open('config.json', 'r') as file:
        start_time_data = json.load(file)
    return start_time_data.get("start_time")


def run_script():
    try:
        logging.info("Executing daily_script.py")
        subprocess.call(["python", "main.py"])
        logging.info("Execution of main.py completed successfully")
    except Exception as e:
        logging.error(f"Error occurred while executing daily_script.py: {e}")

# Load start time from JSON
start_time = load_start_time()

if start_time:
    while True:
        current_time = time.strftime("%H:%M")
        if current_time == start_time:
            run_script()
            # Sleep for 24 hours before checking again
            time.sleep(24 * 60 * 60)
        else:
            # Sleep for 1 minute before checking again
            time.sleep(60)
else:
    logging.error("Start time not loaded. Exiting.")
