from django.urls import path, include
from . import views

urlpatterns = [
    path('checkout', views.checkout, name='checkout'),
    path('billing_info', views.billing_info, name='billing_info'),
    path('process_order', views.process_order, name='process_order'),
    path('payment_success', views.payment_success, name='payment_success'),
    path('payment_failed', views.payment_failed, name='payment_failed'),
    # Shipments
    path('shipped_dashboard', views.shipped_dashboard, name='shipped_dashboard'),
    path('unshipped_dashboard', views.unshipped_dashboard, name='unshipped_dashboard'),
    path('orders/<int:pk>', views.orders, name='orders'),
    # Paypal
    path('paypal', include('paypal.standard.ipn.urls')),
]
