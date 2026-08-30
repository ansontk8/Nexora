from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'product_type', 'is_approved', 'vendor')
    list_filter = ('product_type', 'is_approved', 'category')
    search_fields = ('title', 'category')
