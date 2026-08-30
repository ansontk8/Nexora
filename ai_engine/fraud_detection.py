import joblib
import os
import numpy as np

# Load local ML model
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml_engine', 'models')
CLF_PATH = os.path.join(MODEL_DIR, 'review_classifier.joblib')
VECT_PATH = os.path.join(MODEL_DIR, 'review_vectorizer.joblib')

clf = None
vectorizer = None
_last_loaded_time = 0

def _load_model():
    global clf, vectorizer, _last_loaded_time
    try:
        current_mtime = os.path.getmtime(CLF_PATH)
        if clf is None or vectorizer is None or current_mtime > _last_loaded_time:
            clf = joblib.load(CLF_PATH)
            vectorizer = joblib.load(VECT_PATH)
            _last_loaded_time = current_mtime
            print("ML Model reloaded successfully.")
    except Exception as e:
        if clf is None: # Only error out if we don't have ANY model
            print(f"Error loading ML model: {e}")
            return False
    return True

def analyze_review_authenticity(review_text, rating, user_history=None):
    """
    Analyzes a review for signs of being fake/suspicious using local Random Forest model.
    """
    if not _load_model():
        return {"verdict": "Suspicious", "confidence": 0, "reasoning": "ML model not available"}

    try:
        from scipy.sparse import hstack
        X_text = vectorizer.transform([review_text])
        text_len = len(review_text)
        
        # Cast rating to float to avoid type mismatch errors during hstack
        try:
            numeric_rating = float(rating)
        except (ValueError, TypeError):
            numeric_rating = 3.0 # Default to neutral if invalid
            
        X = hstack((X_text, np.array([[numeric_rating, text_len]])))
        
        verdict = clf.predict(X)[0]
        
        # Get probability for confidence
        try:
            probs = clf.predict_proba(X)
            confidence = int(np.max(probs) * 100)
        except:
            confidence = 100 # Fallback if predict_proba fails
        
        reasoning = f"Local ML analysis identified this review as {verdict} with {confidence}% confidence."
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning,
            "flags": ["ml_flagged"] if verdict != "Genuine" else []
        }
    except Exception as e:
        return {"verdict": "Suspicious", "confidence": 0, "reasoning": f"Error during local analysis: {str(e)}"}
