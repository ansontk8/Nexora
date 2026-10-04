import os
import sys
import django

sys.path.insert(0, r'D:\NEXORA\nexora')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexora.settings')
django.setup()

from products.models import Product

print("--- ALL PRODUCTS ---")
products = Product.objects.all()
for p in products:
    print(f"ID: {p.id}, Title: {p.title}, Category: {p.category}, Type: {p.product_type}, Active: {p.is_active}, Approved: {p.is_approved}")

print("\n--- LAPTOP SEARCH ---")
laptops = Product.objects.filter(title__icontains='laptop')
print(f"Matches count: {laptops.count()}")
for l in laptops:
    print(f"Match: {l.title} - Active: {l.is_active} - Approved: {l.is_approved}")

print("\n--- AI LOGIC ---")
from ai_engine.search import analyze_search_query
try:
    res = analyze_search_query("laptops")
    print("AI Filters:", res)
except Exception as e:
    print("Error calling AI Search:", e)
