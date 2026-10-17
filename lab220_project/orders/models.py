from accounts.models import Address
from django.conf import settings
from django.db import models
from products.models import Product
from vendors.models import Vendor


class Cart(models.Model):
  user = models.OneToOneField(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      null=True,
      blank=True,
      related_name='cart',
  )
  session_key = models.CharField(
      max_length=40,
      blank=True,
      null=True,
      help_text='Identifier for guest visitor carts',
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  @property
  def total_items(self):
    return sum(item.quantity for item in self.items.all())

  @property
  def total_price(self):
    return sum(item.line_total for item in self.items.all())

  def __str__(self):
    if self.user:
      return f"Cart of {self.user.username}"
    return f"Guest Cart ({self.session_key})"


class CartItem(models.Model):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)

  @property
  def line_total(self):
    return self.product.current_price * self.quantity

  def __str__(self):
    return f'{self.quantity}x {self.product.title}'


class Order(models.Model):
  """Master/Parent Order created upon buyer checkout."""

  PAYMENT_STATUS_CHOICES = (
      ('pending', 'Pending'),
      ('paid', 'Paid'),
      ('failed', 'Failed'),
      ('refunded', 'Refunded'),
  )

  PAYMENT_METHOD_CHOICES = (
      ('cod', 'Cash On Delivery'),
      ('card_mock', 'Card Payment (Demo/Mock)'),
  )

  buyer = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.SET_NULL,
      null=True,
      related_name='orders',
  )
  shipping_address = models.ForeignKey(
      Address, on_delete=models.SET_NULL, null=True, related_name='orders'
  )

  total_amount = models.DecimalField(max_digits=10, decimal_places=2)
  payment_method = models.CharField(
      max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod'
  )
  payment_status = models.CharField(
      max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending'
  )
  payment_id = models.CharField(
      max_length=255, blank=True, help_text='Gateway payment reference'
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-created_at']

  def __str__(self):
    return f'Order #{self.id} - ${self.total_amount} ({self.payment_status})'


class VendorOrder(models.Model):
  """Sub-Order scoped to an individual vendor for fulfillment and payout."""

  STATUS_CHOICES = (
      ('pending', 'Pending'),
      ('processing', 'Processing'),
      ('shipped', 'Shipped'),
      ('delivered', 'Delivered'),
      ('cancelled', 'Cancelled'),
  )

  order = models.ForeignKey(
      Order, on_delete=models.CASCADE, related_name='vendor_orders'
  )
  vendor = models.ForeignKey(
      Vendor, on_delete=models.CASCADE, related_name='fulfillment_orders'
  )

  subtotal = models.DecimalField(max_digits=10, decimal_places=2)
  commission_fee = models.DecimalField(
      max_digits=10, decimal_places=2
  )  # Platform revenue
  vendor_earnings = models.DecimalField(
      max_digits=10, decimal_places=2
  )  # Net payout to vendor

  status = models.CharField(
      max_length=20, choices=STATUS_CHOICES, default='pending'
  )
  courier_name = models.CharField(max_length=100, blank=True)
  tracking_number = models.CharField(max_length=100, blank=True)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-created_at']

  def __str__(self):
    return f'SubOrder #{self.id} (Order #{self.order.id}) - {self.vendor.store_name}'


class OrderItem(models.Model):
  """Individual product item tied to the specific Vendor's Sub-Order."""

  vendor_order = models.ForeignKey(
      VendorOrder, on_delete=models.CASCADE, related_name='items'
  )
  product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

  # Snapshots captured at time of order
  product_title = models.CharField(max_length=255)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  quantity = models.PositiveIntegerField(default=1)

  @property
  def line_total(self):
    return self.price * self.quantity

  def __str__(self):
    return f'{self.quantity}x {self.product_title}'
