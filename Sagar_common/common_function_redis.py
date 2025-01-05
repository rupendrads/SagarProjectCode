import json
import os
import sys

def fetch_parameter(env, key):
    file_name = f"config_{env}.json"
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    
    try:
        # Read the JSON config file
        with open(file_path, 'r') as config_file:
            config_data = json.load(config_file)
        
        # Return the required parameter from the config file
        return config_data.get(key)
    
    except FileNotFoundError:
        print(f"Error: {file_name} not found at {file_path}.")
        return None
    except json.JSONDecodeError:
        print(f"Error: {file_name} contains invalid JSON at {file_path}.")
        return None

if __name__ == "__main__":
    # Ensure that we have the right number of arguments
    if len(sys.argv) != 3:
        print("Usage: python common_function.py <env> <key>")
        sys.exit(1)

    env = sys.argv[1]
    key = sys.argv[2]

    result = fetch_parameter(env, key)
    if result:
        print(json.dumps(result))  # Output the result as JSON
    else:
        print(json.dumps({}))  # Return empty JSON if not found
