from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from app.services.gemini_client import analyze_query
from app.api import category, search,source,score,nearby

app = FastAPI()

app.include_router(category.router)
app.include_router(search.router)
app.include_router(source.router)
app.include_router(score.router)
app.include_router(nearby.router)
class QueryInput(BaseModel):
    query: str

@app.post("/analyze")
def analyze(input: QueryInput):
    result = analyze_query(input.query)
    return result

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

