from fastapi import APIRouter, Depends
from app.services.gemini_client import classify_category, rerank_news, generate_summary
from app.services.redis_client import get_redis_client, get_news_by_categories
from datetime import datetime

router = APIRouter()

@router.post("/category")
def get_category_news(query: str, redis=Depends(get_redis_client)):
    # Classify query into categories
    categories = classify_category(query)
    
    # Handle errors in category classification
    if isinstance(categories, dict) and "error" in categories:
        return categories

    # Fetch news based on classified categories
    all_news = get_news_by_categories(redis, categories)

    # Sort news by publication date (desc)
    sorted_news = sorted(
        all_news,
        key=lambda x: datetime.fromisoformat(x["publication_date"]),
        reverse=True
    )

    # Rerank the top 20 news articles
    top_news = rerank_news(query, sorted_news[:20])[:5]

    # Add LLM summary to each article
    for item in top_news:
        item["llm_summary"] = generate_summary(item["title"], item["description"])

    return {
        "categories": categories,
        "results": top_news
    }
