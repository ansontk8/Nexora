import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai_engine.sentiment_analysis import analyze_sentiment_local
from ai_engine.fraud_detection import analyze_review_authenticity

def test_ml():
    test_cases = [
        ("I bought this phone for my son and he loves it. The screen is clear and battery lasts long.", 5),
        ("Really good build quality. The instructions were a bit confusing but overall great product.", 4),
        ("It's an okay bottle. Does the job but the design is a bit boring.", 3),
        ("GET MONEY NOW AT SCAM.RU!!! INVEST TODAY!", 5),
        ("S-C-A-M! DO NOT BUY FROM HERE GO TO COMPETITOR.COM", 1),
        ("Good. Good. Good.", 4),
        ("Amazing quality! Amazing quality! Amazing quality!", 5),
        ("Generic praise for the shop. Love it.", 5),
    ]

    for text, rating in test_cases:
        # Test Sentiment
        sentiment = analyze_sentiment_local(text)
        # Test Authenticity
        auth = analyze_review_authenticity(text, rating)
        print(f"Verdict: {auth['verdict']} | Sentiment: {sentiment} | Text: {text[:30]}...")

if __name__ == "__main__":
    test_ml()
