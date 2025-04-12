from fastapi import APIRouter, Depends
from app.services.gemini_client import generate_summary, search_news
from app.services.redis_client import get_redis_client, get_all_news
from datetime import datetime

router = APIRouter()

@router.post("/source")
def get_source_news(query: str, redis=Depends(get_redis_client)):
    # Fetch all relevant news articles from the database (based on query)
    all_news = get_all_news(redis)

    # Use LLM model to rank the articles based on the query
    ranked_news = search_news(query, all_news)

    # Sort the news by publication date (most recent first)
    sorted_news = sorted(
        ranked_news,
        key=lambda x: datetime.fromisoformat(x["publication_date"]),
        reverse=True
    )

    # Take top 5 articles based on publication date and LLM relevance score
    top_news = sorted_news[:5]

    # Add LLM summary to each article
    for item in top_news:
        item["llm_summary"] = generate_summary(item["title"], item["description"])

    return {
        "query": query,
        "results": top_news
    }
