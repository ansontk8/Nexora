import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from orders.models import Cart, CartItem
from ai_engine.shipping_service import shiprocket
from django.conf import settings

print("--- Shipping Debug (V2) ---")
carts = Cart.objects.all()
for cart in carts:
    print(f"\nUser: {cart.user.username}")
    items = cart.items.all()
    print(f"Total Cart Items: {items.count()}")
    
    for item in items:
        p = item.product
        print(f"  - Item ID: {item.id}, Product: '{p.title}', Type: '{p.product_type}', Fulfillment: '{item.fulfillment_type}'")
    
    physical_items = items.filter(fulfillment_type='physical')
    print(f"Physical Queryset Count: {physical_items.count()}")

    if physical_items.exists():
        print("Calculating rate...")
        res = shiprocket.get_shipping_rate(
            pickup_pincode=settings.SHIPROCKET_PICKUP_PINCODE,
            delivery_pincode='400001',
            weight=0.5 * physical_items.count()
        )
        print(f"ShipRocket Result: {res}")
    else:
        print("No physical items found.")
