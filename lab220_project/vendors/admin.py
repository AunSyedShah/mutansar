from django.contrib import admin
from .models import Payout, Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
  list_display = (
      'store_name',
      'user',
      'commission_rate',
      'is_approved',
      'is_active',
      'created_at',
  )
  list_filter = ('is_approved', 'is_active', 'created_at')
  search_fields = ('store_name', 'user__username', 'user__email')
  prepopulated_fields = {'slug': ('store_name',)}
  actions = ['approve_vendors', 'suspend_vendors']

  @admin.action(description='Approve selected vendors')
  def approve_vendors(self, request, queryset):
    queryset.update(is_approved=True)

  @admin.action(description='Suspend selected vendors')
  def suspend_vendors(self, request, queryset):
    queryset.update(is_active=False)


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
  list_display = (
      'id',
      'vendor',
      'amount',
      'status',
      'requested_at',
      'processed_at',
  )
  list_filter = ('status', 'requested_at')
  search_fields = (
      'vendor__store_name',
      'transaction_reference',
  )
