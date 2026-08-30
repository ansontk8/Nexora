import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def analyze_sentiment(text):
    """
    Analyze sentiment using Groq API.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Analyze the sentiment of the following product review. Return ONLY the word 'Positive', 'Negative', or 'Neutral'."},
                {"role": "user", "content": text}
            ],
            max_tokens=10
        )
        sentiment = response.choices[0].message.content.strip().title()
        if sentiment in ['Positive', 'Negative', 'Neutral']:
            return sentiment
        return "Neutral"
    except Exception as e:
        print(f"Sentiment Analysis Error: {e}")
        return "Neutral"

def detect_fake_advanced(text, rating):
    """
    Analyze review authenticity using Groq API.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": """Analyze this product review for authenticity. 
                Identify if it's 'Genuine', 'Suspicious', or 'Fake'.
                Return a JSON object with keys: 'verdict', 'confidence' (0-100), and 'reasoning'."""},
                {"role": "user", "content": f"Rating: {rating}/5\nReview: {text}"}
            ],
            response_format={"type": "json_object"}
        )
        analysis = json.loads(response.choices[0].message.content)
        return analysis
    except Exception as e:
        print(f"Fraud Detection Error: {e}")
        return {"verdict": "Genuine", "confidence": 0, "reasoning": "AI analysis skipped due to error."}
