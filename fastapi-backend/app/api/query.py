from app.services.gemini_client import analyze_query, generate_summary
from app.services.redis_client import get_redis_client
from app.api import category, score, search, source, nearby
import json
import logging
from fastapi import APIRouter, Depends

router = APIRouter()
logger = logging.getLogger("uvicorn")

intent_router_map = {
    "category": category.get_category_news,
    "score": score.get_scored_news,
    "search": search.search,  # Now directly call search function
    "source": source.get_source_news,
    "nearby": nearby.get_nearby
}

@router.post("/query")
def analyze_and_process_query(query: str, redis=Depends(get_redis_client)):
    logger.info(f"Received query: {query}")

    # Analyze the query using LLM
    analysis_result = analyze_query(query)
    logger.info("Raw Response: %s", analysis_result)

    # Check if analysis_result is a string (since it's plain text, not JSON)
    if isinstance(analysis_result, str):
        # Extract intent and entities manually from the response text
        intent = None
        entities = []
        for line in analysis_result.split("\n"):
            if line.startswith("intent:"):
                intent = line.replace("intent:", "").strip()
            elif line.startswith("entity:"):
                entities.append(line.replace("entity:", "").strip())

        if not intent:
            logger.error("No intent found in the response.")
            return {"error": "No intent found in the response.", "raw_response": analysis_result}

        # Process the result based on the extracted intent and entities
        logger.info(f"Extracted intent: {intent}, entities: {entities}")

        # Get the handler function for the intent
        handler = intent_router_map.get(intent)
        if not handler:
            logger.error(f"Unsupported intent: {intent}")
            return {"error": f"Unsupported intent: {intent}", "raw_response": analysis_result}

        # Call the handler function directly, passing query to it
        result = handler(query=query, redis=redis)

        # Process the result
        combined_results = result.get("results", [])

        # Deduplicate and limit to top 5
        seen_titles = set()
        unique_results = []
        for item in combined_results:
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                item["llm_summary"] = generate_summary(item["title"], item["description"])
                unique_results.append(item)
            if len(unique_results) >= 5:
                break

        return {
            "query": query,
            "results": unique_results
        }

    else:
        # Handle the case if analysis_result is not a string
        logger.error(f"Unexpected response format: {type(analysis_result)}")
        return {"error": "Unexpected response format", "raw_response": str(analysis_result)}
