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
    """
    This function takes a search query and ranks the news articles
    based on the relevance of the query to the news content.
    It uses an LLM model to better match articles with the user's query.
    """
    # Prepare the context for LLM
    context = "\n\n".join([f"Title: {item['title']}\nDescription: {item['description']}" for item in news_items])

    # Prepare the prompt with both the query and the news context
    prompt = f"""
    You are a helpful assistant that ranks news articles based on their relevance to the user's query.

    User Query: "{query}"

    News Articles:
    {context}

    Please respond with the titles of the top 5 most relevant articles, in order of relevance, based on the query.
    Respond only with the titles in JSON array format.
    """
    
    # Generate response from LLM
    response = model.generate_content(prompt)
    
    try:
        # Parse the response text into a list of titles
        top_titles = eval(response.text)
        
        # Rank the news items based on their relevance score calculated by the LLM
        ranked_news = []
        for item in news_items:
            relevance_score = calculate_relevance(query, item)  # Implement a custom relevance calculation if needed
            ranked_news.append({**item, 'relevance_score': relevance_score})
        
        # Sort news by relevance score (descending order)
        ranked_news = sorted(ranked_news, key=lambda x: x['relevance_score'], reverse=True)

        # Return the top 5 articles based on their relevance score
        return ranked_news[:5]

    except Exception as e:
        # In case of any error, return a fallback of the first 5 news items
        print(f"Error processing response: {e}")
        return news_items[:5]

def calculate_relevance(query: str, article: dict) -> float:
    """
    This function calculates a relevance score for a news article based on the user's query.
    The scoring mechanism can be adjusted depending on the complexity you want (e.g., TF-IDF, BERT, etc.).
    """
    # A simple placeholder for relevance calculation (e.g., a basic keyword matching score)
    title_match = query.lower() in article['title'].lower()
    description_match = query.lower() in article['description'].lower()

    # Example: If both title and description match, give a higher score
    relevance_score = 0.7 if title_match else 0.3
    if description_match:
        relevance_score += 0.3

    # Ensure relevance score is between 0 and 1
    relevance_score = min(relevance_score, 1.0)

    return relevance_score