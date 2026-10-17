from django.contrib import admin
from .models import Category, Product, ProductImage, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug', 'parent')
  prepopulated_fields = {'slug': ('name',)}
  search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
  model = ProductImage
  extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = (
      'title',
      'vendor',
      'category',
      'price',
      'discount_price',
      'stock',
      'is_active',
      'is_featured',
  )
  list_filter = ('is_active', 'is_featured', 'category', 'vendor')
  search_fields = ('title', 'description', 'vendor__store_name')
  prepopulated_fields = {'slug': ('title',)}
  inlines = [ProductImageInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
  list_display = ('product', 'buyer', 'rating', 'created_at')
  list_filter = ('rating', 'created_at')
  search_fields = ('product__title', 'buyer__username', 'comment')
