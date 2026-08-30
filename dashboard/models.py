from django.db import models
from accounts.models import User
from products.models import Product

class VendorApproval(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='vendor_reviews')
    reviewed_at = models.DateTimeField(auto_now_add=True)

class ProductApproval(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

class VendorPerformance(models.Model):
    vendor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='performance')
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    delivery_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    complaint_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    response_time = models.DurationField(null=True, blank=True)
    trust_badge = models.CharField(max_length=50, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def calculate_score(self):
        from orders.models import Order, OrderItem
        from reviews.models import Review
        from django.db.models import Avg

        vendor = self.vendor

        # --- Delivery Success Rate ---
        # All orders that contain at least one product from this vendor
        vendor_orders = Order.objects.filter(
            orderitem__product__vendor=vendor
        ).distinct()

        total_orders = vendor_orders.count()
        if total_orders > 0:
            successful = vendor_orders.filter(status__in=['confirmed', 'completed']).count()
            cancelled = vendor_orders.filter(status='cancelled').count()
            self.delivery_success_rate = round((successful / total_orders) * 100, 2)
            self.complaint_ratio = round((cancelled / total_orders) * 100, 2)
        else:
            self.delivery_success_rate = 0.0
            self.complaint_ratio = 0.0

        # --- Average Customer Rating ---
        avg = Review.objects.filter(
            product__vendor=vendor,
            is_fake=False
        ).aggregate(avg=Avg('rating'))['avg']
        self.average_rating = round(avg, 2) if avg else 0.0

        # --- Compute Final Score ---
        # Score = (Delivery% × 0.5) + (Rating/5 × 100 × 0.4) + ((100 - Complaint%) × 0.1)
        delivery_component = float(self.delivery_success_rate) * 0.5
        rating_component = (float(self.average_rating) / 5.0) * 100 * 0.4
        reliability_component = (100 - float(self.complaint_ratio)) * 0.1
        self.score = round(delivery_component + rating_component + reliability_component, 2)

        # --- Trust Badge ---
        if total_orders == 0:
            self.trust_badge = None
        elif self.score >= 85:
            self.trust_badge = "Trusted Seller"
        elif self.score >= 70:
            self.trust_badge = "Reliable Seller"
        elif self.score >= 50:
            self.trust_badge = "Growing Seller"
        else:
            self.trust_badge = None

        self.save()

class StockHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_history')
    change_amount = models.IntegerField()
    reason = models.CharField(max_length=100) # e.g., 'Sale', 'Restock', 'Adjustment'
    created_at = models.DateTimeField(auto_now_add=True)
