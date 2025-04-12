from fastapi import APIRouter, Depends
from app.services.gemini_client import search_news
from app.services.redis_client import get_redis_client, get_all_news
from datetime import datetime

router = APIRouter()

@router.post("/score")
def get_scored_news(query: str, redis=Depends(get_redis_client)):
    """
    Rank articles based on relevance_score in descending order.
    """

    # Fetch all news articles from Redis
    all_news = get_all_news(redis)
    
    # Rank the news articles by relevance_score (descending order)
    scored_news = search_news(query, all_news)
    
    # Sort by relevance_score (descending order) to get the highest relevance first
    sorted_news = sorted(scored_news, key=lambda x: x["relevance_score"], reverse=True)
    
    # Return top 5 ranked articles
    return sorted_news[:5]
