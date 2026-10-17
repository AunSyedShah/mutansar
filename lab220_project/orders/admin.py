from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, VendorOrder


class OrderItemInline(admin.TabularInline):
  model = OrderItem
  extra = 0
  readonly_fields = ('product_title', 'price', 'quantity', 'line_total')


class VendorOrderInline(admin.TabularInline):
  model = VendorOrder
  extra = 0
  readonly_fields = ('vendor', 'subtotal', 'commission_fee', 'vendor_earnings')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = (
      'id',
      'buyer',
      'total_amount',
      'payment_method',
      'payment_status',
      'created_at',
  )
  list_filter = ('payment_status', 'payment_method', 'created_at')
  search_fields = ('id', 'buyer__username', 'payment_id')
  inlines = [VendorOrderInline]


@admin.register(VendorOrder)
class VendorOrderAdmin(admin.ModelAdmin):
  list_display = (
      'id',
      'order',
      'vendor',
      'subtotal',
      'commission_fee',
      'vendor_earnings',
      'status',
      'created_at',
  )
  list_filter = ('status', 'created_at', 'vendor')
  search_fields = ('id', 'order__id', 'vendor__store_name', 'tracking_number')
  inlines = [OrderItemInline]


class CartItemInline(admin.TabularInline):
  model = CartItem
  extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'session_key', 'created_at', 'total_price')
  inlines = [CartItemInline]
