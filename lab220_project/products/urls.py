from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Public catalog & Storefronts
    path('', views.product_list_view, name='list'),
    path('product/<slug:slug>/', views.product_detail_view, name='detail'),
    path('product/<slug:slug>/review/', views.add_product_review, name='add_review'),
    path('store/<slug:slug>/', views.vendor_storefront_view, name='vendor_storefront'),

    # Vendor Portal Catalog Management
    path('vendor/products/', views.vendor_products_list, name='vendor_products'),
    path('vendor/products/create/', views.vendor_product_create, name='vendor_product_create'),
    path('vendor/products/<int:product_id>/edit/', views.vendor_product_edit, name='vendor_product_edit'),
    path('vendor/products/<int:product_id>/delete/', views.vendor_product_delete, name='vendor_product_delete'),
]
