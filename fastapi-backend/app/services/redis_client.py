import redis
import os
from dotenv import load_dotenv

load_dotenv()

def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

def get_news_by_categories(redis_client, categories: list) -> list:
    news_items = []
    for key in redis_client.scan_iter("news:*"):
        news = redis_client.json().get(key)
        if news and any(cat.lower() in [c.lower() for c in news.get("category", [])] for cat in categories):
            news_items.append(news)
    return news_items

# redis_client.py
def get_all_news(redis_client) -> list:
    news_items = []
    for key in redis_client.scan_iter("news:*"):
        news = redis_client.json().get(key)
        if news:
            news_items.append(news)
    return news_items

