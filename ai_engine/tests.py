from django.test import TestCase
from .fraud_detection import analyze_review_authenticity
from .analytics import predict_sales
from products.models import Product
from accounts.models import User

class AIEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.vendor = User.objects.create_user(username='vendor', role='vendor', password='password')
        self.product = Product.objects.create(
            title='Test Product',
            price=10.0,
            product_type='physical',
            vendor=self.vendor,
            stock=10
        )

    def test_fraud_detection_structure(self):
        result = analyze_review_authenticity("This is a great product!", 5)
        self.assertIn('verdict', result)
        self.assertIn('confidence', result)

    def test_sales_prediction_output(self):
        result = predict_sales(self.product)
        self.assertIn('predicted_quantity', result)
        self.assertEqual(result['method'], "90-day Moving Average")
