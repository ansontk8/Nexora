from django.contrib import admin
from .models import Order, OrderItem, DigitalAccess

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('id', 'user__username')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')

@admin.register(DigitalAccess)
class DigitalAccessAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'download_count', 'granted_at')
