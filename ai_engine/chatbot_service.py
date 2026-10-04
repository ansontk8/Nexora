import os
import json
from openai import OpenAI
from django.utils import timezone
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ============================================================
#  SHARED TOOLS
# ============================================================

def check_stock(product_name):
    from products.models import Product
    products = Product.objects.filter(title__icontains=product_name, is_approved=True)
    if not products.exists():
        return json.dumps({"error": "No matching product found."})
    return json.dumps([{
        "id": p.id, "title": p.title, "category": p.category,
        "price": float(p.price), "type": p.product_type,
        "stock": p.stock if p.stock is not None else "Unlimited (Digital)",
        "approved": p.is_approved, "active": p.is_active
    } for p in products[:5]])


# ============================================================
#  CUSTOMER TOOLS
# ============================================================

def get_my_orders(user):
    from orders.models import Order
    orders = Order.objects.filter(user=user).order_by('-created_at')
    res = []
    for o in orders:
        items = [{"product": i.product.title, "qty": i.quantity,
                  "price": float(i.price), "type": i.fulfillment_type}
                 for i in o.orderitem_set.all()]
        res.append({
            "order_id": o.id, "date": o.created_at.strftime("%Y-%m-%d"),
            "total": float(o.total_amount), "status": o.get_dynamic_status(),
            "payment": o.payment_method, "items": items,
            "expected_delivery": str(o.expected_delivery_date) if o.expected_delivery_date else "N/A"
        })
    return json.dumps(res if res else {"message": "No orders found."})


def track_order(order_id, user):
    from orders.models import Order
    from ai_engine.shipping_service import shiprocket
    try:
        order = Order.objects.get(id=order_id, user=user)
        tracking = None
        if order.shiprocket_awb_code:
            tracking = shiprocket.track_shipment(order.shiprocket_awb_code, order=order)
        return json.dumps({
            "order_id": order_id, "status": order.get_dynamic_status(),
            "expected_delivery": str(order.expected_delivery_date) if order.expected_delivery_date else "TBD",
            "awb": order.shiprocket_awb_code or "Not yet assigned",
            "tracking": tracking or "No tracking info yet."
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def cancel_order(order_id, user):
    from orders.models import Order
    try:
        order = Order.objects.get(id=order_id, user=user)
        if order.status == 'cancelled':
            return json.dumps({"error": "Order is already cancelled."})
        if order.is_delivered:
            return json.dumps({"error": "Cannot cancel a delivered order."})
        if timezone.now() > (order.created_at + timedelta(hours=4)):
            return json.dumps({"error": "Order is in transit and cannot be cancelled automatically. Please contact support."})
        order.status = 'cancelled'
        order.save()
        return json.dumps({"success": f"Order #{order_id} has been cancelled."})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_my_profile(user):
    from accounts.models import Address
    addresses = [{"name": a.full_name, "phone": a.phone_number,
                  "address": f"{a.street_address}, {a.city}, {a.state} - {a.pincode}",
                  "default": a.is_default}
                 for a in user.addresses.all()]
    return json.dumps({
        "username": user.username, "email": user.email,
        "name": f"{user.first_name} {user.last_name}".strip(),
        "role": user.role, "addresses": addresses
    })


def get_my_cart(user):
    from orders.models import Cart
    try:
        cart = Cart.objects.get(user=user)
        items = [{"product": i.product.title, "qty": i.quantity,
                  "price": float(i.product.price), "type": i.fulfillment_type}
                 for i in cart.items.all()]
        return json.dumps({"items": items, "total": float(cart.get_total()), "item_count": len(items)})
    except Exception:
        return json.dumps({"items": [], "total": 0})


def get_my_reviews(user):
    from reviews.models import Review
    reviews = Review.objects.filter(user=user).order_by('-created_at')
    return json.dumps([{
        "product": r.product.title, "rating": r.rating,
        "text": r.text[:200], "date": r.created_at.strftime("%Y-%m-%d"),
        "verdict": r.verdict
    } for r in reviews] if reviews.exists() else {"message": "No reviews yet."})


def get_my_downloads(user):
    from orders.models import DigitalAccess
    access = DigitalAccess.objects.filter(user=user)
    return json.dumps([{
        "product": a.product.title, "category": a.product.category,
        "downloads": a.download_count
    } for a in access] if access.exists() else {"message": "No digital purchases yet."})


# ============================================================
#  VENDOR TOOLS
# ============================================================

def get_my_products(user):
    from products.models import Product
    if user.role != 'vendor':
        return json.dumps({"error": "Only vendors can access this."})
    products = Product.objects.filter(vendor=user)
    return json.dumps([{
        "id": p.id, "title": p.title, "category": p.category,
        "price": float(p.price), "type": p.product_type,
        "stock": p.stock if p.stock is not None else "Unlimited",
        "active": p.is_active, "approved": p.is_approved,
        "low_stock_threshold": p.low_stock_threshold
    } for p in products] if products.exists() else {"message": "No products found."})


def get_vendor_orders(user):
    from orders.models import Order, OrderItem
    if user.role != 'vendor':
        return json.dumps({"error": "Only vendors can access this."})
    items = OrderItem.objects.filter(product__vendor=user).select_related('order', 'product')
    orders_map = {}
    for item in items:
        oid = item.order.id
        if oid not in orders_map:
            orders_map[oid] = {
                "order_id": oid,
                "date": item.order.created_at.strftime("%Y-%m-%d"),
                "status": item.order.get_dynamic_status(),
                "customer": item.order.user.username,
                "items": []
            }
        orders_map[oid]["items"].append({
            "product": item.product.title, "qty": item.quantity,
            "price": float(item.price), "type": item.fulfillment_type
        })
    return json.dumps(list(orders_map.values()) if orders_map else {"message": "No orders yet."})


def get_vendor_earnings(user):
    from orders.models import OrderItem
    from django.db.models import Sum, Count
    if user.role != 'vendor':
        return json.dumps({"error": "Only vendors can access this."})
    all_items = OrderItem.objects.filter(product__vendor=user)
    completed = all_items.filter(order__status='completed')
    return json.dumps({
        "total_sales_count": all_items.aggregate(c=Count('id'))['c'],
        "completed_sales_count": completed.aggregate(c=Count('id'))['c'],
        "total_earnings": float(completed.aggregate(s=Sum('price'))['s'] or 0),
        "pending_earnings": float(all_items.exclude(order__status='completed').aggregate(s=Sum('price'))['s'] or 0)
    })


def get_vendor_performance(user):
    from dashboard.models import VendorPerformance
    if user.role != 'vendor':
        return json.dumps({"error": "Only vendors can access this."})
    perf, _ = VendorPerformance.objects.get_or_create(vendor=user)
    perf.calculate_score()
    return json.dumps({
        "score": float(perf.score),
        "delivery_success_rate": float(perf.delivery_success_rate),
        "average_rating": float(perf.average_rating),
        "complaint_ratio": float(perf.complaint_ratio),
        "trust_badge": perf.trust_badge or "None yet"
    })


def get_low_stock_products(user):
    from products.models import Product
    from django.db.models import F
    if user.role != 'vendor':
        return json.dumps({"error": "Only vendors can access this."})
    products = Product.objects.filter(
        vendor=user, stock__isnull=False,
        stock__lte=F('low_stock_threshold')
    )
    return json.dumps([{
        "id": p.id, "title": p.title, "stock": p.stock,
        "threshold": p.low_stock_threshold
    } for p in products] if products.exists() else {"message": "No low-stock products."})


# ============================================================
#  ADMIN TOOLS
# ============================================================

def admin_get_platform_stats(user):
    from accounts.models import User as UserModel
    from products.models import Product
    from orders.models import Order
    from reviews.models import Review
    from django.db.models import Sum
    if user.role != 'admin':
        return json.dumps({"error": "Admin only."})
    return json.dumps({
        "total_users": UserModel.objects.count(),
        "total_customers": UserModel.objects.filter(role='customer').count(),
        "total_vendors": UserModel.objects.filter(role='vendor').count(),
        "total_products": Product.objects.count(),
        "pending_products": Product.objects.filter(is_approved=False, is_active=True).count(),
        "declined_products": Product.objects.filter(is_approved=False, is_active=False).count(),
        "total_orders": Order.objects.count(),
        "completed_orders": Order.objects.filter(status='completed').count(),
        "cancelled_orders": Order.objects.filter(status='cancelled').count(),
        "total_revenue": float(Order.objects.filter(status='completed').aggregate(s=Sum('total_amount'))['s'] or 0),
        "total_reviews": Review.objects.count(),
        "flagged_reviews": Review.objects.filter(verdict__in=['Fake', 'Suspicious']).count()
    })


def admin_get_all_users(user):
    from accounts.models import User as UserModel
    if user.role != 'admin':
        return json.dumps({"error": "Admin only."})
    users = UserModel.objects.all().order_by('-date_joined')[:20]
    return json.dumps([{
        "id": u.id, "username": u.username, "email": u.email,
        "role": u.role, "joined": u.date_joined.strftime("%Y-%m-%d"),
        "active": u.is_active
    } for u in users])


def admin_get_pending_products(user):
    from products.models import Product
    if user.role != 'admin':
        return json.dumps({"error": "Admin only."})
    products = Product.objects.filter(is_approved=False, is_active=True)
    return json.dumps([{
        "id": p.id, "title": p.title, "vendor": p.vendor.username,
        "category": p.category, "price": float(p.price), "type": p.product_type
    } for p in products] if products.exists() else {"message": "No pending products."})


def admin_approve_product(product_id, user):
    from products.models import Product
    if user.role != 'admin':
        return json.dumps({"error": "Admin only."})
    try:
        p = Product.objects.get(id=product_id)
        p.is_approved = True
        p.is_active = True
        p.save()
        return json.dumps({"success": f'Product "{p.title}" (ID {product_id}) has been approved and is now live.'})
    except Exception as e:
        return json.dumps({"error": str(e)})


def admin_decline_product(product_id, user):
    from products.models import Product
    if user.role != 'admin':
        return json.dumps({"error": "Admin only."})
    try:
        p = Product.objects.get(id=product_id)
        p.is_approved = False
        p.is_active = False
        p.save()
        return json.dumps({"success": f'Product "{p.title}" (ID {product_id}) has been declined.'})
    except Exception as e:
        return json.dumps({"error": str(e)})


def admin_get_all_orders(user):
    from orders.models import Order
    if user.role != 'admin':
        return json.dumps({"error": "Admin only."})
    orders = Order.objects.all().order_by('-created_at')[:20]
    return json.dumps([{
        "order_id": o.id, "customer": o.user.username,
        "total": float(o.total_amount), "status": o.get_dynamic_status(),
        "date": o.created_at.strftime("%Y-%m-%d"), "payment": o.payment_method
    } for o in orders])


def admin_get_flagged_reviews(user):
    from reviews.models import Review
    if user.role != 'admin':
        return json.dumps({"error": "Admin only."})
    reviews = Review.objects.filter(verdict__in=['Fake', 'Suspicious']).order_by('-created_at')
    return json.dumps([{
        "id": r.id, "product": r.product.title, "user": r.user.username,
        "rating": r.rating, "verdict": r.verdict,
        "text": r.text[:150], "date": r.created_at.strftime("%Y-%m-%d")
    } for r in reviews] if reviews.exists() else {"message": "No flagged reviews."})


def admin_get_all_vendors(user):
    from accounts.models import User as UserModel
    from orders.models import OrderItem
    from django.db.models import Sum
    if user.role != 'admin':
        return json.dumps({"error": "Admin only."})
    vendors = UserModel.objects.filter(role='vendor')
    result = []
    for v in vendors:
        rev = OrderItem.objects.filter(product__vendor=v, order__status='completed').aggregate(s=Sum('price'))['s']
        result.append({
            "id": v.id, "username": v.username, "email": v.email,
            "total_revenue": float(rev or 0),
            "product_count": v.products.count(),
            "joined": v.date_joined.strftime("%Y-%m-%d")
        })
    return json.dumps(result)


# ============================================================
#  TOOL REGISTRY — role-scoped
# ============================================================

TOOL_DEFINITIONS = {
    "customer": [
        {"type": "function", "function": {
            "name": "get_my_orders",
            "description": "Get all orders placed by the customer, including items, status, total, and delivery info.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "track_order",
            "description": "Track a specific order by ID — returns live status and shipment tracking.",
            "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}}, "required": ["order_id"]}
        }},
        {"type": "function", "function": {
            "name": "cancel_order",
            "description": "Cancel an order by ID (only within 4 hours of placement).",
            "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}}, "required": ["order_id"]}
        }},
        {"type": "function", "function": {
            "name": "get_my_profile",
            "description": "Get the customer's profile details including saved addresses.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "get_my_cart",
            "description": "View the customer's current cart — items, quantities, and total.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "get_my_reviews",
            "description": "Get all reviews written by the customer.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "get_my_downloads",
            "description": "List all digital products the customer has purchased and can download.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "check_stock",
            "description": "Check current stock and price for any product by name.",
            "parameters": {"type": "object", "properties": {"product_name": {"type": "string"}}, "required": ["product_name"]}
        }},
    ],
    "vendor": [
        {"type": "function", "function": {
            "name": "get_my_products",
            "description": "List all products belonging to this vendor — stock, approval status, price.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "get_vendor_orders",
            "description": "List all orders that contain this vendor's products.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "get_vendor_earnings",
            "description": "Get total earnings, completed sales count, and pending earnings for this vendor.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "get_vendor_performance",
            "description": "Get this vendor's performance score, delivery success rate, average rating, and trust badge.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "get_low_stock_products",
            "description": "Get a list of this vendor's products that are at or below their low-stock threshold.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "get_my_profile",
            "description": "Get this vendor's profile and saved addresses.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "check_stock",
            "description": "Check stock and price for any specific product by name.",
            "parameters": {"type": "object", "properties": {"product_name": {"type": "string"}}, "required": ["product_name"]}
        }},
    ],
    "admin": [
        {"type": "function", "function": {
            "name": "admin_get_platform_stats",
            "description": "Get a full snapshot of NEXORA platform — users, products, orders, revenue, reviews.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "admin_get_all_users",
            "description": "Get a list of all registered users (latest 20) with their roles and join dates.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "admin_get_all_vendors",
            "description": "Get all vendors with their revenue, product count, and account info.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "admin_get_pending_products",
            "description": "Get all products awaiting admin approval.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "admin_approve_product",
            "description": "Approve a product by its ID so it goes live on the marketplace.",
            "parameters": {"type": "object", "properties": {"product_id": {"type": "integer"}}, "required": ["product_id"]}
        }},
        {"type": "function", "function": {
            "name": "admin_decline_product",
            "description": "Decline and hide a product by its ID.",
            "parameters": {"type": "object", "properties": {"product_id": {"type": "integer"}}, "required": ["product_id"]}
        }},
        {"type": "function", "function": {
            "name": "admin_get_all_orders",
            "description": "List the most recent 20 orders platform-wide with customer and status info.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "admin_get_flagged_reviews",
            "description": "Get all reviews flagged as Fake or Suspicious by the AI fraud detector.",
            "parameters": {"type": "object", "properties": {}}
        }},
        {"type": "function", "function": {
            "name": "check_stock",
            "description": "Check stock for any product by name.",
            "parameters": {"type": "object", "properties": {"product_name": {"type": "string"}}, "required": ["product_name"]}
        }},
    ]
}

SYSTEM_PROMPTS = {
    "customer": """You are Nexa, the intelligent personal assistant for NEXORA Marketplace.
You are helping {name}, a customer on their dashboard.
You have FULL access to their account data through tools — orders, cart, profile, reviews, digital downloads.
Be helpful, friendly, and proactive. If the user asks about their orders, purchases, deliveries, or downloads — use the appropriate tool immediately.
You can also cancel orders, track shipments, and check product availability.
Policies: Refunds within 14 days for physical, no refunds for digital. Shipping via ShipRocket.
CRITICAL POLICY: ALWAYS format all prices and currency amounts in Indian Rupees (₹). DO NOT use dollars ($).
Always address the user by their name.""",

    "vendor": """You are Nexa, the intelligent business assistant for NEXORA Vendors.
You are helping {name}, a vendor managing their store.
You have FULL access to their vendor data — products, orders, earnings, performance metrics, and low-stock alerts.
Help them understand their business performance, check inventory, review sales, and manage their store efficiently.
Be data-driven and concise. Highlight important metrics like low stock, pending approvals, and earnings.
CRITICAL POLICY: ALWAYS format all prices and currency amounts in Indian Rupees (₹). DO NOT use dollars ($).""",

    "admin": """You are Nexa, the NEXORA Platform Administrator's AI assistant.
You are helping {name}, a platform administrator.
You have FULL administrative access — platform statistics, all users, all vendors, all orders, all reviews.
You can approve or decline products directly. You can surface flagged reviews, pending approvals, and revenue data.
Be precise and executive. Provide summaries and actionable insights when asked.
Confirm before performing irreversible actions like declining products.
CRITICAL POLICY: ALWAYS format all prices and currency amounts in Indian Rupees (₹). DO NOT use dollars ($)."""
}


# ============================================================
#  MAIN ENTRY POINT
# ============================================================

def get_chatbot_response(user_message, user=None, role="customer"):
    role = role.lower() if role else "customer"
    if role not in TOOL_DEFINITIONS:
        role = "customer"

    display_name = "there"
    if user:
        display_name = user.first_name if user.first_name else user.username

    system_prompt = SYSTEM_PROMPTS[role].format(name=display_name)
    tools = TOOL_DEFINITIONS[role]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message)

            for tc in tool_calls:
                fn = tc.function.name
                args = json.loads(tc.function.arguments)

                # Route to the correct tool function
                tool_map = {
                    # Shared
                    "check_stock":              lambda a: check_stock(a.get("product_name")),
                    # Customer
                    "get_my_orders":            lambda a: get_my_orders(user),
                    "track_order":              lambda a: track_order(a.get("order_id"), user),
                    "cancel_order":             lambda a: cancel_order(a.get("order_id"), user),
                    "get_my_profile":           lambda a: get_my_profile(user),
                    "get_my_cart":              lambda a: get_my_cart(user),
                    "get_my_reviews":           lambda a: get_my_reviews(user),
                    "get_my_downloads":         lambda a: get_my_downloads(user),
                    # Vendor
                    "get_my_products":          lambda a: get_my_products(user),
                    "get_vendor_orders":        lambda a: get_vendor_orders(user),
                    "get_vendor_earnings":      lambda a: get_vendor_earnings(user),
                    "get_vendor_performance":   lambda a: get_vendor_performance(user),
                    "get_low_stock_products":   lambda a: get_low_stock_products(user),
                    # Admin
                    "admin_get_platform_stats": lambda a: admin_get_platform_stats(user),
                    "admin_get_all_users":      lambda a: admin_get_all_users(user),
                    "admin_get_all_vendors":    lambda a: admin_get_all_vendors(user),
                    "admin_get_pending_products": lambda a: admin_get_pending_products(user),
                    "admin_approve_product":    lambda a: admin_approve_product(a.get("product_id"), user),
                    "admin_decline_product":    lambda a: admin_decline_product(a.get("product_id"), user),
                    "admin_get_all_orders":     lambda a: admin_get_all_orders(user),
                    "admin_get_flagged_reviews": lambda a: admin_get_flagged_reviews(user),
                }

                if fn in tool_map:
                    result = tool_map[fn](args)
                else:
                    result = json.dumps({"error": f"Unknown tool: {fn}"})

                messages.append({
                    "tool_call_id": tc.id,
                    "role": "tool",
                    "name": fn,
                    "content": result
                })

            second_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )
            return second_response.choices[0].message.content

        return response_message.content

    except Exception as e:
        print(f"Groq API Error: {e}")
        return "Nexa is briefly unavailable. Please try again in a moment."
