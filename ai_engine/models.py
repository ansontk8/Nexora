from django.db import models
from accounts.models import User
from products.models import Product

class AIDescriptionLog(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    keywords = models.TextField()
    product_type = models.CharField(max_length=20)
    ai_title = models.TextField()
    ai_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
