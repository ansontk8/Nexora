from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User

def landing_page(request):
    return render(request, 'landing.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password, role=role)
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next', '')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        user = authenticate(request, username=username, password=password)

        if user is not None and user.role == role:
            login(request, user)

            if next_url:
                return redirect(next_url)

            if role == 'customer':
                return redirect('customer_dashboard')
            elif role == 'vendor':
                return redirect('vendor_dashboard')
            elif role == 'admin':
                return redirect('admin_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials or role mismatch', 'next': next_url})

    return render(request, 'login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('landing')


@login_required
def customer_dashboard(request):
    from ai_engine.recommender import get_recommendations
    from orders.models import Order, OrderItem
    from reviews.models import Review
    from django.db.models import Sum
    
    recommendations = get_recommendations(request.user)
    orders = Order.objects.filter(user=request.user)
    recent_orders = orders.order_by('-created_at') # removed slicing for complete history
    
    total_orders_count = orders.count()
    digital_items_count = OrderItem.objects.filter(order__user=request.user, fulfillment_type='digital').count()
    my_reviews_count = Review.objects.filter(user=request.user).count()
    total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    return render(request, 'dashboard/customer_dashboard.html', {
        'recommendations': recommendations,
        'recent_orders': recent_orders,
        'total_orders_count': total_orders_count,
        'digital_items_count': digital_items_count,
        'my_reviews_count': my_reviews_count,
        'total_spent': total_spent
    })


@login_required
def vendor_dashboard(request):
    from products.models import Product
    from orders.models import OrderItem
    
    products = Product.objects.filter(vendor=request.user)
    # Simple earnings calculation from completed orders
    sales = OrderItem.objects.filter(product__vendor=request.user, order__status='completed')
    total_earnings = sum(item.price * item.quantity for item in sales)
    
    return render(request, 'dashboard/vendor_dashboard.html', {
        'products': products,
        'total_earnings': total_earnings,
        'total_sales': sales.count()
    })



@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        
        if user.role == 'customer':
            return redirect('customer_dashboard')
        elif user.role == 'vendor':
            return redirect('vendor_dashboard')
        else:
            return redirect('admin_dashboard')
            
    return render(request, 'accounts/edit_profile.html')
