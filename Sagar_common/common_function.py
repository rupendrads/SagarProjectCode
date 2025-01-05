import json
import os

def fetch_parameter(env, key):
    file_name = f"config_{env}.json"
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    try:
        with open(file_path, 'r') as config_file:
            config_data = json.load(config_file)
        return config_data.get(key)
    except FileNotFoundError:
        print(f"Error: {file_name} not found at {file_path}.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {file_name} contains invalid JSON at {file_path}.")
        return None


