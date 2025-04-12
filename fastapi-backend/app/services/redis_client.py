import os
import redis
from redis.commands.json import JSON
from dotenv import load_dotenv

load_dotenv()

# Redis connection setup
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0)
redis_json = JSON(redis_client)

def get_news_by_id(news_id: str) -> dict:
    key = f"news:{news_id}"
    try:
        data = redis_json.get(key)
        return data or {"error": "News not found"}
    except Exception as e:
        return {"error": str(e)}
