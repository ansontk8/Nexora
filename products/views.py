from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product

def calculate_delivery_days(distance_km):
    if distance_km <= 50:
        return 1
    elif distance_km <= 200:
        return 3
    elif distance_km <= 500:
        return 5
    else:
        return 7


@login_required
def toggle_availability(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    product.is_active = not product.is_active
    product.save()
    return redirect('vendor_dashboard')

def product_list(request):
    from django.db.models import Q
    
    query = request.GET.get('q')
    products = Product.objects.filter(is_approved=True)
    
    ai_filters = None
    
    if query:
        from django.db.models import Q, Case, When, IntegerField, Value

        # --- Step 1: Try AI-powered structured search ---
        ai_filters = None
        try:
            from ai_engine.search import analyze_search_query
            ai_filters = analyze_search_query(query)
        except Exception:
            pass

        if ai_filters:
            keywords = ai_filters.get('keywords') or query
            expanded = ai_filters.get('expanded_keywords') or []

            # Title+category search: use original query, AI keywords, AND all expanded variants
            # This allows "laptops" to match a product titled "Lenovo laptop"
            def make_title_cat_q(term):
                return (
                    Q(title__icontains=term) |
                    Q(category__icontains=term)
                )

            # Description search: ONLY use the original raw query and the AI-extracted phrase.
            # Do NOT use single expanded words — this prevents common words like "light"
            # from matching unrelated descriptions (e.g., "light grey" in a laptop description).
            def make_desc_q(term):
                return Q(description__icontains=term)

            # Start with title/category match on original query and AI keyword
            search_q = make_title_cat_q(keywords)
            if keywords.lower() != query.lower():
                search_q |= make_title_cat_q(query)

            # Add expanded keywords for title/category only
            for word in expanded[:5]:
                search_q |= make_title_cat_q(word)

            # Add description matching ONLY for the original query phrase and AI keyword phrase
            # (only if term is multi-word or meaningful, to avoid single-character false matches)
            if len(query.strip()) >= 3:
                search_q |= make_desc_q(query)
            if len(keywords.strip()) >= 3 and keywords.lower() != query.lower():
                search_q |= make_desc_q(keywords)

            products = products.filter(search_q)

            # Order by relevance: title match > category match > description match
            products = products.annotate(
                relevance=Case(
                    When(title__icontains=keywords, then=Value(3)),
                    When(title__icontains=query, then=Value(3)),
                    When(category__icontains=keywords, then=Value(2)),
                    When(category__icontains=query, then=Value(2)),
                    When(description__icontains=query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by('-relevance')

            # Hard filters — only apply when user explicitly specified them
            # Protect against AI hallucinations by checking if the query actually implies a price or type
            has_numbers = any(char.isdigit() for char in query)
            if ai_filters.get('price_max') and has_numbers:
                products = products.filter(price__lte=ai_filters['price_max'])
            if ai_filters.get('price_min') and has_numbers:
                products = products.filter(price__gte=ai_filters['price_min'])

            pt = ai_filters.get('product_type')
            if pt and pt in ['digital', 'physical', 'hybrid'] and pt in query.lower():
                products = products.filter(product_type=pt)

        else:
            # Fallback: simple direct text search across all fields
            products = products.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__icontains=query)
            )



    user_distance = 120  # 🔧 mock distance (later from profile / API)

    product_data = []

    from reviews.models import Review
    from django.db.models import Avg, Count

    for p in products:
        delivery_days = None
        if p.product_type == 'physical' or (p.product_type == 'hybrid' and p.physical_delivery_available):
            delivery_days = calculate_delivery_days(user_distance)

        stats = Review.objects.filter(product=p).aggregate(Avg('rating'), Count('id'))
        product_data.append({
            'product': p,
            'delivery_days': delivery_days,
            'avg_rating': stats['rating__avg'] or 0,
            'review_count': stats['id__count'] or 0
        })

    return render(request, 'products/product_list.html', {
        'product_data': product_data,
        'distance': user_distance,
        'search_query': query,
        'ai_filters': ai_filters
    })


@login_required
def add_product(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        price = request.POST.get("price")
        product_type = request.POST.get("product_type")
        physical_delivery_available = request.POST.get("physical_delivery_available")
        image = request.FILES.get("image")
        digital_file = request.FILES.get("file")
        is_template = request.POST.get("is_template") == "on"  # Handles checkbox

        if product_type == "hybrid":
            physical_delivery_available = True if physical_delivery_available == "yes" else False
        else:
            physical_delivery_available = None

        product = Product.objects.create(
            title=title,
            description=description,
            category=category,
            price=price,
            product_type=product_type,
            physical_delivery_available=physical_delivery_available,
            is_template=is_template,  # 👈 NEW
            image=image,
            file=digital_file,
            vendor=request.user,
            is_approved=False
        )

        return redirect("vendor_dashboard")

    return render(request, "products/add_product.html")


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Mock distance for delivery calculation
    user_distance = 120
    delivery_days = None
    if product.product_type == 'physical' or (product.product_type == 'hybrid' and product.physical_delivery_available):
        delivery_days = calculate_delivery_days(user_distance)
        
    from reviews.models import Review
    from django.db.models import Avg, Count
    stats = Review.objects.filter(product=product).aggregate(Avg('rating'), Count('id'))
        
    return render(request, 'products/product_detail.html', {
        'product': product,
        'delivery_days': delivery_days,
        'distance': user_distance,
        'avg_rating': stats['rating__avg'] or 0,
        'review_count': stats['id__count'] or 0
    })

@login_required
def update_stock(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id, vendor=request.user)
        new_stock = request.POST.get("stock")
        if new_stock is not None:
            try:
                new_stock = int(new_stock)
                old_stock = product.stock or 0
                diff = new_stock - old_stock
                product.stock = new_stock
                product.save()
                
                from dashboard.models import StockHistory
                StockHistory.objects.create(
                    product=product,
                    change_amount=diff,
                    reason='Manual Adjustment'
                )
            except (ValueError, TypeError):
                pass
    return redirect('vendor_dashboard')

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    product.delete()
    return redirect('vendor_dashboard')
