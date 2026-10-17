from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('dashboard/', views.vendor_dashboard, name='dashboard'),
    path('settings/', views.vendor_settings, name='settings'),
    path('payouts/', views.vendor_payouts, name='payouts'),
]
