from datetime import datetime, timedelta
from django.db.models import Sum, Avg
from decimal import Decimal

import joblib
import pandas as pd
import numpy as np

def predict_sales(product, days=30):
    """
    ML-powered sales prediction using RandomForestRegressor.
    Falls back to moving average if model is missing.
    """
    from orders.models import OrderItem
    from django.conf import settings
    
    model_path = 'ml_engine/models/sales_forecaster.joblib'
    encoder_path = 'ml_engine/models/category_encoder.joblib'
    
    try:
        # Load ML components
        model = joblib.load(model_path)
        le = joblib.load(encoder_path)
        
        # Prepare feature vector for NEXT month
        # Features: ['category_encoded', 'price', 'day', 'month', 'is_weekend']
        now = datetime.now()
        
        # We'll predict for a "typical week" and scale to 30 days
        weekly_preds = []
        cat_encoded = le.transform([product.category])[0]
        
        for d in range(7):
            test_date = now + timedelta(days=d)
            features = pd.DataFrame([{
                'category_encoded': cat_encoded,
                'price': float(product.price),
                'day': test_date.weekday(),
                'month': test_date.month,
                'is_weekend': 1 if test_date.weekday() >= 5 else 0
            }])
            weekly_preds.append(model.predict(features)[0])
            
        predicted_daily = np.mean(weekly_preds)
        predicted_total = round(predicted_daily * days)
        method = "RandomForest Regression (ML)"
        confidence = "High" if len(OrderItem.objects.filter(product=product)) > 10 else "Medium"
        
    except Exception as e:
        # Fallback to Moving Average
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        historical_sales = OrderItem.objects.filter(
            product=product,
            order__created_at__range=(start_date, end_date),
            order__status='completed'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        predicted_total = round((float(historical_sales) / 90.0) * days)
        method = "Moving Average (Fallback)"
        confidence = "Low"

    # ShipRocket Estimation Integration
    from .shipping_service import shiprocket
    ship_res = shiprocket.get_shipping_rate(
        pickup_pincode=settings.SHIPROCKET_PICKUP_PINCODE,
        delivery_pincode='400001', 
        weight=1.0
    )
    est_days = ship_res.get('est_delivery_days', 3)

    return {
        "predicted_quantity": max(1, int(predicted_total)),
        "confidence": confidence,
        "method": method,
        "est_delivery_days": est_days,
        "range": f"{int(predicted_total * 0.8)}-{int(predicted_total * 1.2)}",
        "expected_revenue": float(product.price) * float(predicted_total)
    }

def update_vendor_score(vendor_performance_obj):
    """
    Triggers recalculation of the vendor performance score.
    """
    # In a real app, this would query orders/reviews
    # Here we trigger the internal method
    vendor_performance_obj.calculate_score()
