import redis
import json

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Fetch all keys matching a pattern (use "*" for all keys)
keys = r.keys('*')

# Initialize a dictionary to store key-value pairs
data = {}

# Iterate through the keys
for key in keys:
    key_type = r.type(key)  # Get the type of the key
    if key_type == 'string':
        data[key] = r.get(key)  # Get string value
    elif key_type == 'hash':
        data[key] = r.hgetall(key)  # Get hash values
    elif key_type == 'list':
        data[key] = r.lrange(key, 0, -1)  # Get all list elements
    elif key_type == 'set':
        data[key] = list(r.smembers(key))  # Convert set to list
    elif key_type == 'zset':
        data[key] = r.zrange(key, 0, -1, withscores=True)  # Get sorted set with scores
    else:
        data[key] = f"Unsupported type: {key_type}"

# Save to JSON file
with open('export.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Export completed.")
