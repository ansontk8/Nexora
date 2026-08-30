from django.contrib import admin
from .models import VendorApproval, ProductApproval

@admin.register(VendorApproval)
class VendorApprovalAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'status', 'reviewed_by', 'reviewed_at')
    list_filter = ('status',)

@admin.register(ProductApproval)
class ProductApprovalAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'status', 'reviewed_by', 'reviewed_at')
    list_filter = ('status',)
