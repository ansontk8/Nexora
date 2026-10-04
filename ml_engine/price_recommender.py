import joblib
import os
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
PRICING_MODEL_PATH = os.path.join(MODEL_DIR, 'pricing_optimizer.joblib')

model = None

def _load_pricing_model():
    global model
    if model is None:
        if os.path.exists(PRICING_MODEL_PATH):
            model = joblib.load(PRICING_MODEL_PATH)
        else:
            return None
    return model

def get_price_suggestion(base_price, category_name, stock_level):
    """
    Returns a suggested price based on the local ML model.
    """
    clf = _load_pricing_model()
    if clf is None:
        return base_price # Fallback to original price
    
    # Map category to ID (mocking the mapping used during training)
    cat_map = {
        'Electronics': 0,
        'Fashion': 1,
        'Home': 2,
        'Digital': 3
    }
    cat_id = cat_map.get(category_name, 0)
    
    # Seasonal factor (mocking current season as 'neutral' 1.0)
    # In a real app, this would be derived from the current date
    season_factor = 1.0 
    
    # Features: [base_price, category_id, seasonal_factor, stock_level]
    features = np.array([[base_price, cat_id, season_factor, stock_level]])
    
    try:
        suggested = clf.predict(features)[0]
        return round(float(suggested), 2)
    except:
        return base_price
