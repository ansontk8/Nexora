from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Review
from products.models import Product
from orders.models import Order

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Direct lookup of the OrderItem for this product and user
    # We allow reviews for any order that is NOT cancelled or pending
    from orders.models import OrderItem
    items = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exclude(order__status__in=['pending', 'cancelled'])
    
    order_item = items.first()
    
    if not order_item:
        # Fallback for digital templates: check DigitalAccess directly
        from orders.models import DigitalAccess
        if DigitalAccess.objects.filter(user=request.user, product=product).exists():
            # Find the most recent non-cancelled order for this product
            order_item = OrderItem.objects.filter(
                order__user=request.user,
                product=product
            ).exclude(order__status='cancelled').order_by('-order__created_at').first()

    if not order_item:
        return redirect('customer_dashboard')
        
    order = order_item.order
        
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        
        Review.objects.create(
            user=request.user,
            product=product,
            order=order,
            rating=rating,
            text=text
        )
        return redirect('customer_dashboard')
        
    return render(request, 'reviews/add_review.html', {'product': product})
