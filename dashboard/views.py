from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from accounts.models import User
from products.models import Product
from orders.models import Order
from reviews.models import Review


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('login')

    reviews = Review.objects.all()
    total_reviews = reviews.count()

    flagged_reviews = Review.objects.filter(verdict__in=['Fake', 'Suspicious']).order_by('-created_at')
    for r in flagged_reviews:
        r.username = r.user.username
        r.verdict_upper = r.verdict.upper()
        r.text_short = r.text[:100]
        r.product_title = r.product.title[:30]

    # Top Vendors by Sales Revenue
    from django.db.models import Sum
    from orders.models import OrderItem
    
    vendor_sales = OrderItem.objects.filter(
        order__status='completed',
        product__vendor__role='vendor'
    ).values('product__vendor').annotate(
        total_sales=Sum('price')
    ).order_by('-total_sales')[:5]
    
    top_vendors = []
    for vs in vendor_sales:
        vendor = User.objects.get(id=vs['product__vendor'])
        vendor.total_revenue = vs['total_sales']
        top_vendors.append(vendor)

    context = {
        'total_users': User.objects.count(),
        'total_vendors': User.objects.filter(role='vendor').count(),
        'total_products': Product.objects.count(),
        'pending_products': Product.objects.filter(is_approved=False).count(),
        'total_orders': Order.objects.count(),
        'total_reviews': total_reviews,
        'flagged_reviews': flagged_reviews,
        'top_vendors': top_vendors,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def vendor_list(request):
    if request.user.role != 'admin':
        return redirect('login')

    vendors = User.objects.filter(role='vendor')
    return render(request, 'dashboard/vendor_list.html', {'vendors': vendors})


@login_required
def approve_vendor(request, id):
    if request.user.role != 'admin':
        return redirect('login')

    vendor = get_object_or_404(User, id=id, role='vendor')
    vendor.is_approved = True
    vendor.save()
    return redirect('vendor_list')


@login_required
def product_list(request):
    if request.user.role != 'admin':
        return redirect('login')

    products = Product.objects.all()
    return render(request, 'dashboard/product_list.html', {'products': products})


@login_required
def approve_product(request, id):
    if request.user.role != 'admin':
        return redirect('login')

    product = get_object_or_404(Product, id=id)
    product.is_approved = True
    product.is_active = True
    product.save()
    return redirect('admin_product_list')


@login_required
def decline_product(request, id):
    if request.user.role != 'admin':
        return redirect('login')

    product = get_object_or_404(Product, id=id)
    product.is_approved = False
    product.is_active = False  # Hide from marketplace
    product.save()
    return redirect('admin_product_list')


@login_required
def remove_product(request, id):
    if request.user.role != 'admin':
        return redirect('login')

    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('admin_product_list')


@login_required
def user_list(request):
    if request.user.role != 'admin':
        return redirect('login')

    users = User.objects.all()
    return render(request, 'dashboard/user_list.html', {'users': users})


@login_required
def delete_user(request, id):
    if request.user.role != 'admin':
        return redirect('login')

    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('user_list')


@login_required
def order_list(request):
    if request.user.role != 'admin':
        return redirect('login')

    orders = Order.objects.all()
    return render(request, 'dashboard/order_list.html', {'orders': orders})


@login_required
def review_list(request):
    if request.user.role != 'admin':
        return redirect('login')
    
    reviews = Review.objects.all().order_by('-created_at')
    for r in reviews:
        r.username = r.user.username
        r.verdict_upper = r.verdict.upper()
        r.text_short = r.text[:100]
        r.product_title = r.product.title[:30]
        
    return render(request, 'dashboard/review_list.html', {'reviews': reviews})

@login_required
def delete_review(request, id):
    if request.user.role != 'admin':
        return redirect('login')
    
    review = get_object_or_404(Review, id=id)
    review.delete()
    return redirect('review_list')

@login_required
def vendor_dashboard(request):
    if request.user.role != 'vendor':
        return redirect('login')

    from ai_engine.analytics import predict_sales
    from .models import VendorPerformance, StockHistory
    from ml_engine.price_recommender import get_price_suggestion

    # ML Sales Prediction for Vendor
    vendor_products = Product.objects.filter(vendor=request.user)
    prediction_data = []
    total_projected_revenue = 0
    total_projected_quantity = 0

    from ai_engine.analytics import predict_sales
    for p in vendor_products:
        pred = predict_sales(p)
        total_projected_revenue += pred['expected_revenue']
        total_projected_quantity += pred['predicted_quantity']
        prediction_data.append({
            'product': p.title,
            'quantity': pred['predicted_quantity'],
            'revenue': pred['expected_revenue'],
            'confidence': pred['confidence']
        })

    # Calculate actual earnings and sales from completed orders
    from django.db.models import Sum, Count
    from orders.models import OrderItem
    
    vendor_order_items = OrderItem.objects.filter(
        product__vendor=request.user,
        order__status='completed'
    )
    
    total_earnings = vendor_order_items.aggregate(total=Sum('price'))['total'] or 0
    total_sales = vendor_order_items.aggregate(count=Count('id'))['count'] or 0

    performance, _ = VendorPerformance.objects.get_or_create(vendor=request.user)
    performance.calculate_score()

    low_stock_products = vendor_products.filter(stock__lte=models.F('low_stock_threshold'), product_type__in=['physical', 'hybrid'])
    
    # Add dynamic price suggestions to products
    from ml_engine.price_recommender import get_price_suggestion
    for p in vendor_products:
        p.suggested_price = get_price_suggestion(float(p.price), p.category, p.stock or 0)

    context = {
        'products': vendor_products,
        'performance': performance,
        'low_stock_products': low_stock_products,
        'recent_stock_history': StockHistory.objects.filter(product__vendor=request.user).order_by('-created_at')[:10],
        'total_earnings': total_earnings,
        'total_sales': total_sales,
        'sales_forecast': {
            'total_quantity': total_projected_quantity,
            'total_revenue': total_projected_revenue,
            'items': prediction_data[:5]
        }
    }
    return render(request, 'dashboard/vendor_dashboard.html', context)


@login_required
def delete_order(request, id):
    if request.user.role != 'admin':
        return redirect('login')

    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect('order_list')
