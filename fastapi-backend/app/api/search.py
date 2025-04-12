from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.gemini_client import search_news, generate_summary
from app.services.redis_client import get_redis_client, get_all_news

# Define the SearchRequest model directly in this file
class SearchRequest(BaseModel):
    query: str

router = APIRouter()

@router.post("/search")
def search(request: SearchRequest, redis=Depends(get_redis_client)):
    query = request.query  # Extract the query from the request object

    # Fetch all news articles from Redis
    all_news = get_all_news(redis)

    # Rank the news based on the query
    ranked_news = search_news(query, all_news)

    # Add LLM summary to each of the top ranked news articles
    for item in ranked_news:
        item["llm_summary"] = generate_summary(item["title"], item["description"])

    return {
        "query": query,
        "results": ranked_news
    }
