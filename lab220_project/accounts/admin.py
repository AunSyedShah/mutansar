from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Address, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
  list_display = (
      'username',
      'email',
      'is_buyer',
      'is_vendor',
      'is_staff',
      'is_active',
  )
  list_filter = ('is_buyer', 'is_vendor', 'is_staff', 'is_active')
  fieldsets = BaseUserAdmin.fieldsets + (
      ('Multi-Vendor Roles', {'fields': ('is_buyer', 'is_vendor', 'phone_number', 'avatar')}),
  )
  add_fieldsets = BaseUserAdmin.add_fieldsets + (
      ('Multi-Vendor Roles', {'fields': ('is_buyer', 'is_vendor', 'phone_number', 'avatar')}),
  )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
  list_display = ('user', 'full_name', 'phone', 'city', 'country', 'is_default')
  search_fields = ('user__username', 'full_name', 'phone', 'city')
