from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Cart
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),

    # Checkout & Buyer Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<int:order_id>/success/', views.order_success_view, name='order_success'),
    path('my-orders/', views.buyer_orders_view, name='buyer_orders'),
    path('my-orders/<int:order_id>/', views.buyer_order_detail_view, name='buyer_order_detail'),

    # Vendor Fulfillment Portal
    path('vendor/orders/', views.vendor_orders_list, name='vendor_orders'),
    path('vendor/orders/<int:suborder_id>/', views.vendor_order_detail, name='vendor_order_detail'),
]
