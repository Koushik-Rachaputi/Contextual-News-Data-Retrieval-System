import requests
from math import radians, sin, cos, sqrt, atan2
from fastapi import APIRouter, Depends
from app.services.gemini_client import generate_summary, search_news
from app.services.redis_client import get_redis_client, get_all_news

router = APIRouter()

# Fetch user location via IP Geolocation
def get_user_location_from_ip():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        location = data.get("loc", "").split(",")
        lat, lon = float(location[0]), float(location[1])
        return lat, lon
    except Exception as e:
        print(f"Error fetching location: {e}")
        return None, None

# Haversine formula to calculate distance between two lat/lon points
def haversine(lat1, lon1, lat2, lon2):
    # Radius of Earth in kilometers
    R = 6371.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c  # Distance in kilometers
    return distance

# Endpoint to fetch relevant news and rank by proximity
@router.post("/nearby")
def get_nearby(query: str, redis=Depends(get_redis_client)):
    # Get user location
    user_lat, user_lon = get_user_location_from_ip()

    if user_lat is None or user_lon is None:
        return {"error": "Unable to fetch user location"}

    # Fetch all relevant news articles (this can be based on the query or all articles)
    all_news = get_all_news(redis)

    # Use LLM model to rank the articles based on the query
    ranked_news = search_news(query, all_news)

    # Calculate distance and add it to the news articles
    for item in ranked_news:
        news_lat = item.get("latitude")  # Assuming latitude is available in the article data
        news_lon = item.get("longitude")  # Assuming longitude is available in the article data

        if news_lat and news_lon:
            distance = haversine(user_lat, user_lon, news_lat, news_lon)
            item["distance"] = distance

    # Sort news articles by distance (ascending order)
    sorted_news = sorted(ranked_news, key=lambda x: x.get("distance", float("inf")))

    # Return the top 5 news articles with LLM summary
    top_news = sorted_news[:5]

    # Add LLM summary to each article
    for item in top_news:
        item["llm_summary"] = generate_summary(item["title"], item["description"])

    return {
        "query": query,
        "results": top_news
    }
