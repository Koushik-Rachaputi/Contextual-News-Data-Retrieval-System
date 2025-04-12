from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from app.services.gemini_client import analyze_query
from app.api import category, search,source

app = FastAPI()

app.include_router(category.router)
app.include_router(search.router)
app.include_router(source.router)
class QueryInput(BaseModel):
    query: str

@app.post("/analyze")
def analyze(input: QueryInput):
    result = analyze_query(input.query)
    return result

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

@app.post("/score")
def post_score(item_id: int, score: float):
    return {"item_id": item_id, "score": score, "status": "saved"}

@app.get("/nearby")
def get_nearby(lat: float, lon: float, radius_km: float = 5):
    return {
        "location": {"lat": lat, "lon": lon},
        "radius_km": radius_km,
        "results": ["place1", "place2"]
    }
