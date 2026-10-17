from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from vendors.models import Vendor


class Category(models.Model):
  name = models.CharField(max_length=100)
  slug = models.SlugField(max_length=120, unique=True, blank=True)
  icon = models.CharField(
      max_length=50, blank=True, help_text='Icon name or CSS class'
  )
  parent = models.ForeignKey(
      'self',
      null=True,
      blank=True,
      on_delete=models.CASCADE,
      related_name='subcategories',
  )

  class Meta:
    verbose_name_plural = 'Categories'
    ordering = ['name']

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name


class Product(models.Model):
  vendor = models.ForeignKey(
      Vendor, on_delete=models.CASCADE, related_name='products'
  )
  category = models.ForeignKey(
      Category, on_delete=models.SET_NULL, null=True, related_name='products'
  )
  title = models.CharField(max_length=255)
  slug = models.SlugField(max_length=280, unique=True, blank=True)
  description = models.TextField()

  price = models.DecimalField(max_digits=10, decimal_places=2)
  discount_price = models.DecimalField(
      max_digits=10, decimal_places=2, null=True, blank=True
  )
  stock = models.PositiveIntegerField(default=0)

  is_active = models.BooleanField(
      default=True, help_text='Controls whether product appears in store'
  )
  is_featured = models.BooleanField(default=False)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-created_at']

  @property
  def current_price(self):
    if self.discount_price and self.discount_price > 0:
      return self.discount_price
    return self.price

  @property
  def primary_image(self):
    primary = self.images.filter(is_primary=True).first()
    if primary:
      return primary.image
    first_image = self.images.first()
    return first_image.image if first_image else None

  def save(self, *args, **kwargs):
    if not self.slug:
      base_slug = slugify(f'{self.vendor.store_name}-{self.title}')
      slug = base_slug
      counter = 1
      while Product.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1
      self.slug = slug
    super().save(*args, **kwargs)

  def __str__(self):
    return f'{self.title} ({self.vendor.store_name})'


class ProductImage(models.Model):
  product = models.ForeignKey(
      Product, on_delete=models.CASCADE, related_name='images'
  )
  image = models.ImageField(upload_to='products/')
  alt_text = models.CharField(max_length=200, blank=True)
  is_primary = models.BooleanField(default=False)

  def __str__(self):
    return f'Image for {self.product.title}'


class Review(models.Model):
  product = models.ForeignKey(
      Product, on_delete=models.CASCADE, related_name='reviews'
  )
  buyer = models.ForeignKey(
      settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews'
  )
  rating = models.PositiveSmallIntegerField(
      validators=[MinValueValidator(1), MaxValueValidator(5)]
  )
  comment = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ('product', 'buyer')
    ordering = ['-created_at']

  def __str__(self):
    return f'{self.product.title} - {self.rating}★ by {self.buyer.username}'
