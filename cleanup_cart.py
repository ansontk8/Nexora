import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from orders.models import CartItem
from products.models import Product

print("--- Cart Fulfillment Cleanup ---")
items = CartItem.objects.all()
for item in items:
    pt = item.product.product_type.lower()
    if pt == 'physical' and item.fulfillment_type != 'physical':
        print(f"Updating Item {item.id} ('{item.product.title}') to 'physical'")
        item.fulfillment_type = 'physical'
        item.save()
    elif pt == 'digital' and item.fulfillment_type != 'digital':
        print(f"Updating Item {item.id} ('{item.product.title}') to 'digital'")
        item.fulfillment_type = 'digital'
        item.save()

print("Cleanup complete.")
