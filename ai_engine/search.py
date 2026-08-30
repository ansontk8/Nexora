import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def analyze_search_query(query):
    """
    Uses Groq to extract structured filters from a natural language query.
    Returns a dict with: keywords, expanded_keywords, category, price_max, price_min, product_type.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a smart product search assistant for an e-commerce store. "
                        "Analyze the user's search query and return ONLY a JSON object. "
                        "Rules:\n"
                        "- 'keywords': the core search term (keep it specific, e.g. 'table lamp')\n"
                        "- 'expanded_keywords': 3-5 close synonyms/variants ONLY, including singular/plural forms if applicable (e.g., 'laptop', 'macbook', 'laptops'). Do NOT add unrelated product types.\n"
                        "- 'category': the most specific product category (e.g. 'lighting', 'electronics'). null if unclear.\n"
                        "- 'price_max': max price as number ONLY IF EXPLICITLY mentioned in query, else null.\n"
                        "- 'price_min': min price as number ONLY IF EXPLICITLY mentioned in query, else null.\n"
                        "- 'product_type': 'digital', 'physical', or 'hybrid' ONLY IF EXPLICITLY implied or stated, else null.\n"
                        "Return ONLY the JSON object, no explanation."
                    )
                },
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"AI Search Error: {e}")
        return {"keywords": query}
