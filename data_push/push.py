import redis
import json

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Load data from JSON file (with UTF-8 encoding!)
with open('news_data.json', 'r', encoding='utf-8') as f:
    news_items = json.load(f)

# Push each item into Redis
for item in news_items:
    key = f"news:{item['id']}"  # Unique key using the ID
    r.execute_command('JSON.SET', key, '$', json.dumps(item))
    print(f"✅ Stored {key}")
