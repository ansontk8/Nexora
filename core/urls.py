from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from accounts import views as account_views
from products import views as product_views
from ai_engine import views as ai_views
from dashboard import views as dashboard_views
from orders import views as order_views
from reviews import views as review_views





urlpatterns = [

    path('', account_views.landing_page, name='landing'),

    path('register/', account_views.register, name='register'),
    path('login/', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),
    path('profile/edit/', account_views.edit_profile, name='edit_profile'),

    path("admin/dashboard/", dashboard_views.admin_dashboard, name="admin_dashboard"),
    path("admin/vendors/", dashboard_views.vendor_list, name="vendor_list"),
    path("admin/vendors/<int:id>/approve/", dashboard_views.approve_vendor, name="approve_vendor"),
    path("admin/products/", dashboard_views.product_list, name="admin_product_list"),
    path("admin/products/<int:id>/approve/", dashboard_views.approve_product, name="approve_product"),
    path("admin/products/<int:id>/decline/", dashboard_views.decline_product, name="decline_product"),
    path("admin/products/<int:id>/remove/", dashboard_views.remove_product, name="remove_product"),
    path("admin/users/", dashboard_views.user_list, name="user_list"),
    path("admin/users/<int:id>/delete/", dashboard_views.delete_user, name="delete_user"),
    path("admin/orders/", dashboard_views.order_list, name="order_list"),
    path("admin/orders/<int:id>/delete/", dashboard_views.delete_order, name="delete_order"),
    path("admin/reviews/", dashboard_views.review_list, name="review_list"),
    path("admin/reviews/<int:id>/delete/", dashboard_views.delete_review, name="delete_review"),

    path('dashboard/customer/', account_views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/vendor/', dashboard_views.vendor_dashboard, name='vendor_dashboard'),

    path('products/', product_views.product_list, name='product_list'),
    path('products/<int:product_id>/', product_views.product_detail, name='product_view_detail'),
    path('products/<int:product_id>/toggle-availability/', product_views.toggle_availability, name='toggle_availability'),
    path('vendor/add-product/', product_views.add_product, name='add_product'),
    path('products/<int:product_id>/update-stock/', product_views.update_stock, name='update_stock'),


    path("ai/generate-description/", ai_views.generate_description, name="generate_description"),
    path("ai/chat/", ai_views.chat_api, name="chat_api"),
    
    path('cart/', order_views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', order_views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', order_views.remove_from_cart, name='remove_from_cart'),
    
    path('checkout/address/', order_views.checkout_address, name='checkout_address'),
    path('checkout/payment/', order_views.checkout_payment, name='checkout_payment'),
    path('checkout/place-order/', order_views.place_order, name='place_order'),

    path('order/<int:order_id>/', order_views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', order_views.cancel_order, name='cancel_order'),
    path('products/<int:product_id>/delete/', product_views.delete_product, name='delete_product'),
    path('download/<int:product_id>/', order_views.download_file, name='download_file'),
    path('reviews/add/<int:product_id>/', review_views.add_review, name='add_review'),
    
    # PWA Support
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/json'), name='manifest_json'),
    path('service-worker.js', TemplateView.as_view(template_name='js/service-worker.js', content_type='application/javascript'), name='service_worker_js'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
