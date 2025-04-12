import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.services.redis_client import get_all_news
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

CATEGORIES = [
    "DEFENCE", "EXPLAINERS", "FINANCE", "Feel_Good_Stories", "General",
    "Health___Fitness", "IPL", "IPL_2025", "Israel-Hamas_War", "Lifestyle",
    "Russia-Ukraine_Conflict", "automobile", "bollywood", "business", "city",
    "cricket", "crime", "education", "entertainment", "facts", "fashion",
    "football", "hatke", "miscellaneous", "national", "politics", "science",
    "sports", "startup", "technology", "travel", "world"
]

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
    try:
        return eval(response.text)
    except Exception:
        return {"error": "Failed to parse response", "raw_response": response.text}



def classify_category(query: str) -> list:
    prompt = f"""
You are a smart assistant that classifies news-related user queries into the most relevant categories.

Choose from the following categories:
{", ".join(CATEGORIES)}

Input query: "{query}"

Respond ONLY with a list of the best-matching category names in JSON format. Example:
["technology", "science"]
"""
    response = model.generate_content(prompt)
    try:
        return eval(response.text)
    except Exception:
        return {"error": "Failed to parse response", "raw_response": response.text}


def rerank_news(query: str, news_items: list) -> list:
    context = "\n\n".join([
        f"Title: {item['title']}\nDescription: {item['description']}" for item in news_items
    ])

    prompt = f"""
You are a helpful assistant that selects the 5 most relevant news items based on the following user query.

User Query: "{query}"

News Articles:
{context}

Respond with the top 5 article titles (exactly as shown above) in JSON list format.
"""
    response = model.generate_content(prompt)
    try:
        top_titles = eval(response.text)
        # Filter the original items by title match
        return [item for item in news_items if item["title"] in top_titles]
    except Exception:
        return news_items[:5]

def generate_summary(title: str, description: str) -> str:
    prompt = f"""You are a helpful assistant. Summarize the following article in 1-2 concise sentences.
Title: {title}
Description: {description}

Summary:"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Summary not available."

def search_news(query: str, news_items: list) -> list:
    context = "\n\n".join([
        f"Title: {item['title']}\nDescription: {item['description']}" for item in news_items
    ])

    prompt = f"""
    You are a helpful assistant that ranks news articles based on their relevance to the user's query.

    User Query: "{query}"

    News Articles:
    {context}

    Please respond with the titles of the top 5 most relevant articles, in order of relevance, based on the query.
    Respond only with the titles in JSON array format.
    """
    
    response = model.generate_content(prompt)
    
    try:
        top_titles = eval(response.text)

        # Assign LLM relevance score to top 10 articles for better combination
        top_news = [item for item in news_items if item["title"] in top_titles]

        scored_news = []
        for item in top_news:
            llm_score = calculate_llm_relevance(query, item)
            existing_score = item.get("relevance_score", 0.0)
            final_score = (llm_score + existing_score) / 2  # Weighted average can be customized

            scored_news.append({
                **item,
                "llm_relevance_score": llm_score,
                "final_score": final_score
            })

        # Sort by final_score
        return sorted(scored_news, key=lambda x: x["final_score"], reverse=True)[:5]

    except Exception as e:
        print(f"Error processing response: {e}")
        return news_items[:5]

def calculate_llm_relevance(query: str, article: dict) -> float:
    # Simple scoring logic; can be expanded
    title_match = query.lower() in article['title'].lower()
    desc_match = query.lower() in article['description'].lower()
    score = 0.7 if title_match else 0.3
    if desc_match:
        score += 0.3
    return min(score, 1.0)

