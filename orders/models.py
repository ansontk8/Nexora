from django.db import models
from accounts.models import User
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Shipping & Payment
    shipping_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    
    # ShipRocket Tracking
    shiprocket_shipment_id = models.CharField(max_length=100, null=True, blank=True)
    shiprocket_awb_code = models.CharField(max_length=100, null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    # Cancellation window: 6 hours from order creation
    CANCEL_WINDOW_HOURS = 6

    @property
    def cancel_deadline(self):
        from django.utils import timezone
        from datetime import timedelta
        return self.created_at + timedelta(hours=self.CANCEL_WINDOW_HOURS)

    @property
    def can_cancel(self):
        from django.utils import timezone
        if self.status not in ('confirmed', 'pending'):
            return False
        return timezone.now() < self.cancel_deadline

    @property
    def is_delivered(self):
        from django.utils import timezone
        if not self.expected_delivery_date:
            return True # Default to delivered if no date set (legacy orders)
        return timezone.now().date() >= self.expected_delivery_date

    def get_dynamic_status(self):
        if self.status == 'cancelled':
            return 'CANCELLED'
        # Check if order is fully digital or has no shipping info (completed instantly)
        has_physical = self.orderitem_set.filter(fulfillment_type='physical').exists()
        if not has_physical or self.is_delivered:
            return 'COMPLETED'
        return 'IN TRANSIT'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    fulfillment_type = models.CharField(max_length=20, choices=(('digital', 'Digital'), ('physical', 'Physical')), default='physical')

class DigitalAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    download_count = models.IntegerField(default=0)
    granted_at = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return sum(item.get_cost() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    fulfillment_type = models.CharField(max_length=20, choices=(('digital', 'Digital'), ('physical', 'Physical')), default='physical')

    def get_cost(self):
        return self.product.price * self.quantity
