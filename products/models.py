from django.db import models
from accounts.models import User

class Product(models.Model):
    PRODUCT_TYPE = (
        ('digital', 'Digital'),
        ('physical', 'Physical'),
        ('hybrid', 'Hybrid'),   # 👈 NEW
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE)

    # Digital-only
    file = models.FileField(upload_to='digital_products/', null=True, blank=True)

    # Physical-only
    stock = models.IntegerField(null=True, blank=True)

    # Hybrid-specific
    physical_delivery_available = models.BooleanField(null=True, blank=True)

    # AI image input
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)  # 👈 NEW: For Canva-style/editable files
    created_at = models.DateTimeField(auto_now_add=True)

    # Stock Management
    low_stock_threshold = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.product_type == 'physical' and self.stock is not None:
            if self.stock <= 0:
                self.is_active = False
            else:
                self.is_active = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
