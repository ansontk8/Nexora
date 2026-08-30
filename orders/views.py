from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, DigitalAccess, Cart, CartItem
from products.models import Product
from django.db import transaction

@login_required
def add_to_cart(request, product_id):
    if request.user.role != 'customer':
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Selling and Administrative accounts cannot purchase products.")

    product = get_object_or_404(Product, id=product_id)
    fulfillment_type = request.GET.get('fulfillment_type', 'physical')

    # Validation: if digital/physical only, force correct type
    pt = product.product_type.lower()
    if pt == 'digital':
        fulfillment_type = 'digital'
    elif pt == 'physical':
        fulfillment_type = 'physical'

    # --- Stock check for physical fulfillment (covers both physical and hybrid products) ---
    if fulfillment_type == 'physical':
        if product.stock is not None and product.stock <= 0:
            from django.contrib import messages
            messages.error(request, f'"{product.title}" — the physical edition is out of stock.')
            return redirect('product_list')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        fulfillment_type=fulfillment_type
    )
    if not created:
        # Check if adding one more would exceed available stock
        if fulfillment_type == 'physical' and product.stock is not None:
            if item.quantity >= product.stock:
                from django.contrib import messages
                messages.error(request, f'Only {product.stock} units of "{product.title}" are available.')
                return redirect('view_cart')
        item.quantity += 1
        item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'orders/cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('view_cart')

@login_required
def checkout_address(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        return redirect('product_list')

    # Check if the cart contains any physical items that need delivery
    has_physical = cart.items.filter(fulfillment_type='physical').exists()

    # Digital-only cart: skip address step entirely
    if not has_physical:
        request.session['checkout_address_id'] = None
        request.session['total_shipping'] = 0
        return redirect('checkout_payment')

    addresses = request.user.addresses.all()
    if request.method == "POST":
        address_id = request.POST.get('address_id')

        if not address_id:
            return render(request, 'orders/checkout_address.html', {
                'addresses': addresses,
                'error': 'Please select an address.',
                'has_physical': True,
            })

        if address_id == 'new':
            from accounts.models import Address
            full_name = request.POST.get('full_name')
            phone_number = request.POST.get('phone_number')
            street_address = request.POST.get('street_address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pincode = request.POST.get('pincode')

            if not all([full_name, phone_number, street_address, city, state, pincode]):
                return render(request, 'orders/checkout_address.html', {
                    'addresses': addresses,
                    'error': 'Please fill all address fields.',
                    'has_physical': True,
                })

            address = Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone_number=phone_number,
                street_address=street_address,
                city=city,
                state=state,
                pincode=pincode
            )
        else:
            try:
                address = get_object_or_404(request.user.addresses, id=address_id)
            except (ValueError, TypeError):
                return redirect('checkout_address')

        # Calculate Shipping via ShipRocket
        from ai_engine.shipping_service import shiprocket
        from django.conf import settings

        total_shipping = 0
        physical_weight = 0.5

        physical_items = cart.items.filter(fulfillment_type='physical')
        first_item = physical_items.first()
        vendor = first_item.product.vendor
        vendor_address = vendor.addresses.filter(is_default=True).first() or vendor.addresses.first()
        pickup_pincode = vendor_address.pincode if vendor_address else settings.SHIPROCKET_PICKUP_PINCODE

        res = shiprocket.get_shipping_rate(
            pickup_pincode=pickup_pincode,
            delivery_pincode=address.pincode,
            weight=physical_weight * physical_items.count()
        )
        res['pickup_pincode'] = pickup_pincode
        total_shipping = res.get('rate', 0)
        request.session['shipping_info'] = res

        request.session['checkout_address_id'] = address.id
        request.session['total_shipping'] = float(total_shipping)
        return redirect('checkout_payment')

    return render(request, 'orders/checkout_address.html', {
        'addresses': addresses,
        'has_physical': True,
    })

@login_required
def checkout_payment(request):
    # Allow digital-only carts (checkout_address_id may be None)
    if 'checkout_address_id' not in request.session:
        return redirect('checkout_address')

    cart = request.user.cart
    shipping_cost = request.session.get('total_shipping', 0)
    grand_total = float(cart.get_total()) + shipping_cost
    has_physical = cart.items.filter(fulfillment_type='physical').exists()

    from datetime import datetime, timedelta
    shipping_info = request.session.get('shipping_info', {})
    est_days = shipping_info.get('est_delivery_days', 3)
    est_delivery_date = datetime.now() + timedelta(days=est_days) if has_physical else None

    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        expected_delivery_date = request.POST.get('expected_delivery_date')
        request.session['payment_method'] = payment_method
        request.session['expected_delivery_date'] = expected_delivery_date
        return redirect('place_order')

    return render(request, 'orders/checkout_payment.html', {
        'cart': cart,
        'shipping_cost': shipping_cost,
        'total': grand_total,
        'est_delivery_date': est_delivery_date,
        'has_physical': has_physical,
    })

@login_required
def place_order(request):
    if request.user.role != 'customer':
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Selling and Administrative accounts cannot purchase products.")

    address_id = request.session.get('checkout_address_id')  # Can be None for digital-only
    payment_method = request.session.get('payment_method')
    shipping_cost = request.session.get('total_shipping', 0)
    expected_delivery_date = request.session.get('expected_delivery_date')

    # Only require address for physical orders; digital-only can proceed without one
    if not payment_method:
        return redirect('checkout_address')
    
    cart = request.user.cart
    if not cart.items.exists():
        return redirect('product_list')
    
    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            total_amount=float(cart.get_total()) + shipping_cost,
            shipping_address_id=address_id if address_id else None,
            payment_method=payment_method,
            expected_delivery_date=expected_delivery_date if address_id else None,
            status='confirmed'
        )
        
        # ... (OrderItem creation, stock deduction same as before)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                fulfillment_type=item.fulfillment_type
            )
            
            if item.fulfillment_type == 'physical' and item.product.stock is not None:
                item.product.stock -= item.quantity
                item.product.save()
                from dashboard.models import StockHistory
                StockHistory.objects.create(
                    product=item.product,
                    change_amount=-item.quantity,
                    reason=f"Sale - Order #{order.id}"
                )
            
            if item.fulfillment_type == 'digital':
                DigitalAccess.objects.get_or_create(user=request.user, product=item.product)

        # ShipRocket Integration: Create Shipment
        from ai_engine.shipping_service import shiprocket
        if cart.items.filter(fulfillment_type='physical').exists():
            shiprocket_res = shiprocket.create_shipment(order)
            if shiprocket_res.get('status') == 'success':
                order.shiprocket_shipment_id = shiprocket_res.get('shipment_id')
                order.shiprocket_awb_code = shiprocket_res.get('awb_code')
                order.save()
            print(f"ShipRocket Shipment Created: {shiprocket_res.get('shipment_id')}")

        # Clear cart and session
        cart.items.all().delete()
        del request.session['checkout_address_id']
        del request.session['payment_method']
        if 'total_shipping' in request.session: del request.session['total_shipping']
        if 'shipping_info' in request.session: del request.session['shipping_info']
        
    return redirect('order_detail', order_id=order.id)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)
    
    tracking_details = None
    if order.shiprocket_awb_code:
        from ai_engine.shipping_service import shiprocket
        tracking_details = shiprocket.track_shipment(order.shiprocket_awb_code, order=order)
        
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items,
        'tracking': tracking_details
    })

@login_required
def download_file(request, product_id):
    access = get_object_or_404(DigitalAccess, user=request.user, product_id=product_id)
    product = access.product
    
    if not product.file:
        return redirect('customer_dashboard')
        
    access.download_count += 1
    access.save()
    
    # In a real app, use FileResponse with secure storage path
    return redirect(product.file.url)


@login_required
def cancel_order(request, order_id):
    """Cancel an order within the 6-hour cancellation window."""
    if request.method != 'POST':
        return redirect('order_detail', order_id=order_id)

    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Hard check: window must still be open
    if not order.can_cancel:
        from django.contrib import messages
        messages.error(request, "The cancellation window for this order has expired.")
        return redirect('order_detail', order_id=order_id)

    with transaction.atomic():
        # Restore stock for physical items
        for item in order.orderitem_set.filter(fulfillment_type='physical'):
            if item.product.stock is not None:
                item.product.stock += item.quantity
                item.product.save()
                from dashboard.models import StockHistory
                StockHistory.objects.create(
                    product=item.product,
                    change_amount=item.quantity,
                    reason=f"Cancellation - Order #{order.id}"
                )

        order.status = 'cancelled'
        order.save()

    from django.contrib import messages
    messages.success(request, f"Order #ORD-{order.id} has been successfully cancelled.")
    return redirect('order_detail', order_id=order_id)
