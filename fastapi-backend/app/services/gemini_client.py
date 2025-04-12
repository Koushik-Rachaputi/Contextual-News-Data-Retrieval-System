# app/services/gemini_client.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def analyze_query(query: str) -> dict:
    prompt = f"""
    You are an intelligent assistant that extracts:
    - Intent (what the user wants)
    - Entities (named things like people, organizations, or places)

    INTENT DEFINITIONS:
    - "category": Retrieve articles from a specific category (e.g., "Technology", "Business", "Sports").
    - "score": Retrieve articles with a relevance_score above a threshold (e.g., 0.7).
    - "search": Perform a text search in article titles/descriptions.
    - "source": Retrieve articles from specific sources (e.g., "New York Times", "Reuters").
    - "nearby": Retrieve articles near a specific location (from the query).

    INSTRUCTIONS:
    Given the input query, return a JSON with exactly:
    {{
    "intent": ["list of intents"],
    "entities": ["list of named entities"]
    }}

    Input Query: "{query}"
    Respond ONLY with valid JSON. No explanations.
    """

    response = model.generate_content(prompt)
    cleaned = response.text.strip().strip("```json").strip("```")
    
    try:
        return json.loads(cleaned)
    except Exception:
        return {
            "error": "Failed to parse response",
            "raw_response": response.text
        }
