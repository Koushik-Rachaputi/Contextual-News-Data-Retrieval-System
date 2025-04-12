import redis
import json

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Get all keys matching your news pattern
keys = r.keys('news:*')
keys = r.keys('news:*')
print("Found keys:", keys)

# Set to hold all unique categories
all_categories = set()

# Loop through all news items
for key in keys:
    item_json = r.execute_command('JSON.GET', key, '$')
    item_data = json.loads(item_json)[0]  # JSON.GET returns a JSON array at root path $
    
    categories = item_data.get('category', [])
    all_categories.update(categories)

# Show all unique categories
print("🗂️ All Categories:")
for cat in sorted(all_categories):
    print("-", cat)
