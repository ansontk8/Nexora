from django.db import models
from accounts.models import User
from products.models import Product
from orders.models import Order

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.IntegerField()
    text = models.TextField()
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    is_fake = models.BooleanField(default=False)
    verdict = models.CharField(max_length=20, default='Genuine') # Genuine, Suspicious, Fake
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Always run analysis if it's a new review or for development/testing transparency
        # In production, we'd check if text changed.
        from .services import analyze_sentiment, detect_fake_advanced
        self.sentiment = analyze_sentiment(self.text)
        
        analysis = detect_fake_advanced(self.text, self.rating)
        self.verdict = analysis.get('verdict', 'Genuine')
        self.is_fake = (self.verdict == 'Fake')
            
        super().save(*args, **kwargs)
