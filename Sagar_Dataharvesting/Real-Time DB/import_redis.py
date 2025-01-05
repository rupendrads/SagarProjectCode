import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

with open('export.json', 'r') as f:
    data = json.load(f)

for key, value in data.items():
    if isinstance(value, str):
        r.set(key, value)
    elif isinstance(value, dict):
        r.hmset(key, value)
    elif isinstance(value, list):
        for item in value:
            r.rpush(key, item)
    elif isinstance(value, list) and all(isinstance(v, tuple) for v in value):
        for member, score in value:
            r.zadd(key, {member: score})
    else:
        print(f"Unsupported data type for key: {key}")

print("Import completed.")
