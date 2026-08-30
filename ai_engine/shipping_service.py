import requests
import json
from django.conf import settings
from datetime import datetime, timedelta

class ShipRocketService:
    def __init__(self):
        self.email = getattr(settings, 'SHIPROCKET_EMAIL', None)
        self.password = getattr(settings, 'SHIPROCKET_PASSWORD', None)
        self.base_url = "https://apiv2.shiprocket.in/v1/external"
        self.token = None
        self.token_expiry = None

    def _get_token(self):
        """
        Authenticate with ShipRocket and cache the JWT token.
        """
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.token

        if not self.email or not self.password or 'example.com' in self.email:
            # Fallback for development if credentials are empty or placeholders
            return "MOCK_TOKEN"

        url = f"{self.base_url}/auth/login"
        payload = {"email": self.email, "password": self.password}
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                # Tokens usually last 24 hours, expires in 10 days actually, but let's be safe
                self.token_expiry = datetime.now() + timedelta(days=1)
                return self.token
        except Exception as e:
            print(f"ShipRocket Auth Error: {e}")
        
        return None

    def get_shipping_rate(self, pickup_pincode, delivery_pincode, weight, length=10, width=10, height=10):
        """
        Fetch shipping rates for a given route and weight.
        """
        token = self._get_token()
        if not token or token == "MOCK_TOKEN":
            # Mock pricing logic if in dev or token fails
            try:
                p_pin = int(pickup_pincode)
                d_pin = int(delivery_pincode)
                distance_est = abs(d_pin - p_pin) / 1000
                rate = max(40, 40 + (distance_est * 0.5) + (float(weight) * 10))
                return {
                    "status": 200,
                    "rate": round(rate, 2),
                    "courier_name": "NEXORA Express (Mock)",
                    "est_delivery_days": max(1, min(7, int(distance_est / 100)))
                }
            except (ValueError, TypeError):
                return {
                    "status": 200,
                    "rate": 50.0, # Flat rate fallback
                    "courier_name": "NEXORA Express (Flat Rate)",
                    "est_delivery_days": 3
                }

        url = f"{self.base_url}/courier/serviceability/"
        params = {
            "pickup_pincode": pickup_pincode,
            "delivery_pincode": delivery_pincode,
            "weight": weight,
            "cod": 1 # Standard
        }
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Find the cheapest available courier
                available = data.get('data', {}).get('available_courier_companies', [])
                if available:
                    cheapest = min(available, key=lambda x: float(x['rate']))
                    return {
                        "status": 200,
                        "rate": float(cheapest['rate']),
                        "courier_name": cheapest['courier_name'],
                        "est_delivery_days": cheapest.get('etd_hours', 24) // 24
                    }
        except Exception as e:
            print(f"ShipRocket Rate Error: {e}")

        return {"status": 500, "error": "Serviceability check failed"}

    def create_shipment(self, order):
        """
        Pushes an order to ShipRocket for fulfillment.
        """
        token = self._get_token()
        if not token or token == "MOCK_TOKEN":
            # Mock successful shipment for development
            return {
                "status": "success", 
                "shipment_id": f"SR_{order.id}_123", 
                "awb_code": f"AWB_{order.id}_XY"
            }

        # Implementation for generating a real shipment object would go here
        # Requires mapping Order/OrderItem to ShipRocket's API structure
        return {"status": "pending", "message": "Real shipment creation requires production environment"}

    def track_shipment(self, awb_code, order=None):
        """
        Get tracking details for a specific AWB.
        """
        token = self._get_token()
        if not token or token == "MOCK_TOKEN":
            # Use Order date if available, otherwise now
            base_date = order.created_at if order else datetime.now()
            dest_city = order.shipping_address.city if (order and order.shipping_address) else "Mumbai Hub"
            
            history = [
                {
                    "date": base_date, 
                    "status": "Picked Up", 
                    "location": "Vendor Warehouse"
                },
                {
                    "date": base_date + timedelta(hours=4), 
                    "status": "In Transit", 
                    "location": f"{dest_city} Processing Center"
                }
            ]

            # Logic for delivery day
            if order and order.expected_delivery_date:
                from django.utils import timezone
                # Create a datetime for the expected delivery date at 10 AM
                delivery_dt_morning = datetime.combine(order.expected_delivery_date, datetime.min.time()) + timedelta(hours=10)
                delivery_dt_afternoon = delivery_dt_morning + timedelta(hours=4)
                
                # Check if system time has reached the delivery date
                if timezone.now().date() >= order.expected_delivery_date:
                    history.append({
                        "date": delivery_dt_morning,
                        "status": "Out for Delivery",
                        "location": f"{dest_city} Last Mile Hub"
                    })
                    history.append({
                        "date": delivery_dt_afternoon,
                        "status": "Delivered",
                        "location": "Customer Doorstep"
                    })
                elif (order.expected_delivery_date - timezone.now().date()).days <= 1:
                    # If it's tomorrow, show as Out for Delivery if today is late enough
                    history.append({
                        "date": delivery_dt_morning if timezone.now().date() == order.expected_delivery_date else timezone.now(),
                        "status": "In Transit",
                        "location": f"En route to {dest_city}"
                    })

            return {
                "status": "Delivered" if (order and order.is_delivered) else "In Transit",
                "current_location": dest_city,
                "history": history,
                "tracking_url": f"https://shiprocket.co/tracking/{awb_code}"
            }

        url = f"{self.base_url}/courier/track/awb/{awb_code}"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Tracking Error: {e}")
        
        return {"error": "Tracking details unavailable"}

# Singleton instance
shiprocket = ShipRocketService()
