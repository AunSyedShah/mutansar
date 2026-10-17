from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/buyer/', views.register_buyer, name='register_buyer'),
    path('register/vendor/', views.register_vendor, name='register_vendor'),
    path('vendor/pending/', views.vendor_pending_view, name='vendor_pending'),
    path('addresses/', views.addresses_view, name='addresses'),
    path('addresses/<int:address_id>/delete/', views.address_delete_view, name='address_delete'),
]
