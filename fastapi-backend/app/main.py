from fastapi import FastAPI, Query
from typing import Optional
from app.services.gemini_client import analyze_query
from pydantic import BaseModel
from app.services.redis_client import get_news_by_id
app = FastAPI()

class QueryInput(BaseModel):
    query: str

class NewsQuery(BaseModel):
    news_id: str

@app.post("/get-news/")
async def get_news(query: NewsQuery):
    result = get_news_by_id(query.news_id)
    return result

@app.post("/analyze")
def analyze(input: QueryInput):
    result = analyze_query(input.query)
    return result

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

@app.get("/category")
def get_category():
    return {"categories": ["food", "entertainment", "shopping", "health"]}

@app.post("/score")
def post_score(item_id: int, score: float):
    return {"item_id": item_id, "score": score, "status": "saved"}

@app.get("/source")
def get_source():
    return {"source": "Internal DB", "updated": "2025-04-12"}

@app.get("/search")
def search(q: Optional[str] = Query(None, min_length=2)):
    results = ["example1", "example2"] if q else []
    return {"query": q, "results": results}

@app.get("/nearby")
def get_nearby(lat: float, lon: float, radius_km: float = 5):
    return {
        "location": {"lat": lat, "lon": lon},
        "radius_km": radius_km,
        "results": ["place1", "place2"]
    }
