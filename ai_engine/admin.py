from django.contrib import admin
from .models import AIDescriptionLog, UserActivity

@admin.register(AIDescriptionLog)
class AIDescriptionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'product_name', 'category', 'product_type', 'created_at')

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'action_type', 'created_at')
