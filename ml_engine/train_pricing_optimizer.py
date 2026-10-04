import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import numpy as np

def train_pricing_model():
    # In a real app, we'd pull from OrderItem.
    # For now, if OrderItem is empty, we'll generate synthetic data based on reasonable pricing rules.
    
    # Check if we have enough real data (mocking the check)
    data_points = []
    
    # Rule-based synthetic data generation for the core "NEXORA" products
    # Features: [base_price, category_id, seasonal_factor, stock_level]
    # Categories: 0: Electronics, 1: Fashion, 2: Home, 3: Digital
    
    for _ in range(500):
        category = np.random.randint(0, 4)
        base = np.random.uniform(500, 5000)
        stock = np.random.randint(0, 100)
        season = np.random.uniform(0.8, 1.5)
        
        # Target: Ideal Price
        # Rule: If stock is low, price can go up. If it's holiday season, price can go up.
        price_mod = season
        if stock < 10: price_mod += 0.2
        
        ideal_price = base * price_mod
        data_points.append([base, category, season, stock, ideal_price])
        
    df = pd.DataFrame(data_points, columns=['base_price', 'category_id', 'seasonal_factor', 'stock_level', 'ideal_price'])
    
    X = df[['base_price', 'category_id', 'seasonal_factor', 'stock_level']]
    y = df['ideal_price']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Regressor for Dynamic Pricing...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, 'pricing_optimizer.joblib'))
    
    print(f"Pricing model saved to {model_dir}")

if __name__ == "__main__":
    train_pricing_model()
