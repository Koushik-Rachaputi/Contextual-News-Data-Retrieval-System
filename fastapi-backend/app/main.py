from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from app.services.gemini_client import analyze_query
from app.api import category, search,source,score,nearby,query

app = FastAPI()

app.include_router(category.router)
app.include_router(search.router)
app.include_router(source.router)
app.include_router(score.router)
app.include_router(nearby.router)
app.include_router(query.router)
class QueryInput(BaseModel):
    query: str


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

