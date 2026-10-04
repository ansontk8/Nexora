import os
import django
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
from datetime import datetime, timedelta

# Setup Django
import sys
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from orders.models import OrderItem
from products.models import Product

def train_sales_model():
    print("Extracting sales data...")
    
    # Query all completed order items
    items = OrderItem.objects.filter(order__status='completed').select_related('order', 'product')
    
    if not items.exists():
        print("No sales data available. Training skipped.")
        return False
        
    data = []
    for item in items:
        data.append({
            'product_id': item.product.id,
            'category': item.product.category,
            'price': float(item.price),
            'quantity': item.quantity,
            'day': item.order.created_at.weekday(),
            'month': item.order.created_at.month,
            'is_weekend': 1 if item.order.created_at.weekday() >= 5 else 0
        })
        
    df = pd.DataFrame(data)
    
    # Feature Engineering
    le = LabelEncoder()
    df['category_encoded'] = le.fit_transform(df['category'])
    
    # Features: category_encoded, price, day, month, is_weekend
    X = df[['category_encoded', 'price', 'day', 'month', 'is_weekend']]
    y = df['quantity']
    
    print(f"Training on {len(df)} samples...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save resources
    os.makedirs('ml_engine/models', exist_ok=True)
    joblib.dump(model, 'ml_engine/models/sales_forecaster.joblib')
    joblib.dump(le, 'ml_engine/models/category_encoder.joblib')
    
    print("Model trained and saved successfully.")
    return True

if __name__ == "__main__":
    train_sales_model()
