from decimal import Decimal
from accounts.decorators import buyer_required, vendor_required
from accounts.models import Address
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem, VendorOrder


def get_or_create_cart(request):
  """Helper to retrieve or initialize a cart for either authenticated user or guest session."""
  if request.user.is_authenticated:
    cart, _ = Cart.objects.get_or_create(user=request.user)
    # If guest had a session cart before logging in, merge it
    if request.session.session_key:
      guest_cart = Cart.objects.filter(
          session_key=request.session.session_key
      ).first()
      if guest_cart and guest_cart != cart:
        for item in guest_cart.items.all():
          existing_item = cart.items.filter(product=item.product).first()
          if existing_item:
            existing_item.quantity += item.quantity
            existing_item.save()
          else:
            item.cart = cart
            item.save()
        guest_cart.delete()
    return cart
  else:
    if not request.session.session_key:
      request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_view(request):
  cart = get_or_create_cart(request)
  items = cart.items.select_related('product__vendor').all()

  # Group cart items by vendor for clear UI visualization
  vendor_groups = {}
  for item in items:
    vendor = item.product.vendor
    if vendor not in vendor_groups:
      vendor_groups[vendor] = []
    vendor_groups[vendor].append(item)

  return render(
      request,
      'orders/cart.html',
      {
          'cart': cart,
          'items': items,
          'vendor_groups': vendor_groups,
      },
  )


def cart_add(request, product_id):
  product = get_object_or_404(Product, id=product_id, is_active=True)
  cart = get_or_create_cart(request)

  quantity = int(request.POST.get('quantity', 1))
  if quantity < 1:
    quantity = 1

  cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
  if not created:
    cart_item.quantity += quantity
  else:
    cart_item.quantity = quantity

  if cart_item.quantity > product.stock:
    cart_item.quantity = product.stock
    messages.warning(
        request, f'Adjusted quantity to max available stock ({product.stock}).'
    )

  cart_item.save()
  messages.success(request, f'Added "{product.title}" to your cart.')
  return redirect(request.META.get('HTTP_REFERER', 'orders:cart_view'))


def cart_update(request, item_id):
  cart = get_or_create_cart(request)
  cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

  quantity = int(request.POST.get('quantity', 1))
  if quantity > 0:
    if quantity <= cart_item.product.stock:
      cart_item.quantity = quantity
      cart_item.save()
      messages.success(request, 'Cart updated.')
    else:
      messages.warning(
          request,
          f'Only {cart_item.product.stock} units available for'
          f' {cart_item.product.title}.',
      )
  else:
    cart_item.delete()
    messages.info(request, 'Item removed from cart.')

  return redirect('orders:cart_view')


def cart_remove(request, item_id):
  cart = get_or_create_cart(request)
  cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
  cart_item.delete()
  messages.info(request, 'Item removed from cart.')
  return redirect('orders:cart_view')


@buyer_required
def checkout_view(request):
  cart = get_or_create_cart(request)
  items = cart.items.select_related('product__vendor').all()

  if not items.exists():
    messages.warning(request, 'Your cart is currently empty.')
    return redirect('products:list')

  addresses = Address.objects.filter(user=request.user)

  # Group by vendor
  vendor_groups = {}
  for item in items:
    vendor = item.product.vendor
    if vendor not in vendor_groups:
      vendor_groups[vendor] = []
    vendor_groups[vendor].append(item)

  if request.method == 'POST':
    address_id = request.POST.get('address_id')
    payment_method = request.POST.get('payment_method', 'cod')

    if not address_id:
      messages.error(
          request, 'Please select or add a shipping address to proceed.'
      )
      return render(
          request,
          'orders/checkout.html',
          {
              'cart': cart,
              'items': items,
              'vendor_groups': vendor_groups,
              'addresses': addresses,
          },
      )

    shipping_address = get_object_or_404(
        Address, id=address_id, user=request.user
    )

    with transaction.atomic():
      # 1. Create Master Parent Order
      master_order = Order.objects.create(
          buyer=request.user,
          shipping_address=shipping_address,
          total_amount=cart.total_price,
          payment_method=payment_method,
          payment_status='paid' if payment_method == 'card_mock' else 'pending',
          payment_id=(
              f'MOCK-PAY-{master_order_id_placeholder(cart.id)}'
              if payment_method == 'card_mock'
              else ''
          ),
      )

      # 2. Split Order across each vendor
      for vendor, vendor_items in vendor_groups.items():
        subtotal = sum(item.line_total for item in vendor_items)
        # Calculate platform fee commission
        commission_rate = vendor.commission_rate
        commission_fee = round(
            Decimal(subtotal) * (Decimal(commission_rate) / Decimal(100)), 2
        )
        vendor_earnings = Decimal(subtotal) - commission_fee

        vendor_order = VendorOrder.objects.create(
            order=master_order,
            vendor=vendor,
            subtotal=subtotal,
            commission_fee=commission_fee,
            vendor_earnings=vendor_earnings,
            status='pending',
        )

        # 3. Create frozen line item snapshots and reduce inventory stock
        for item in vendor_items:
          OrderItem.objects.create(
              vendor_order=vendor_order,
              product=item.product,
              product_title=item.product.title,
              price=item.product.current_price,
              quantity=item.quantity,
          )
          # Decrement inventory stock
          item.product.stock = max(0, item.product.stock - item.quantity)
          item.product.save()

      # 4. Clear the Cart
      cart.items.all().delete()

    messages.success(
        request, 'Your order was successfully placed across verified sellers!'
    )
    return redirect('orders:order_success', order_id=master_order.id)

  return render(
      request,
      'orders/checkout.html',
      {
          'cart': cart,
          'items': items,
          'vendor_groups': vendor_groups,
          'addresses': addresses,
      },
  )


def master_order_id_placeholder(seed):
  import random

  return f'{seed}{random.randint(1000, 9999)}'


@buyer_required
def order_success_view(request, order_id):
  order = get_object_or_404(
      Order.objects.prefetch_related('vendor_orders__items', 'vendor_orders__vendor'),
      id=order_id,
      buyer=request.user,
  )
  return render(request, 'orders/order_success.html', {'order': order})


@buyer_required
def buyer_orders_view(request):
  orders = (
      Order.objects.filter(buyer=request.user)
      .prefetch_related('vendor_orders__vendor')
      .order_by('-created_at')
  )
  return render(request, 'orders/buyer_orders.html', {'orders': orders})


@buyer_required
def buyer_order_detail_view(request, order_id):
  order = get_object_or_404(
      Order.objects.prefetch_related(
          'vendor_orders__items', 'vendor_orders__vendor'
      ),
      id=order_id,
      buyer=request.user,
  )
  return render(request, 'orders/buyer_order_detail.html', {'order': order})


# ==========================================
# VENDOR ORDER FULFILLMENT VIEWS
# ==========================================


@vendor_required
def vendor_orders_list(request):
  vendor = request.user.vendor_profile
  vendor_orders = (
      VendorOrder.objects.filter(vendor=vendor)
      .select_related('order__buyer', 'order__shipping_address')
      .prefetch_related('items')
      .order_by('-created_at')
  )

  status_filter = request.GET.get('status')
  if status_filter:
    vendor_orders = vendor_orders.filter(status=status_filter)

  return render(
      request,
      'orders/vendor_orders.html',
      {
          'vendor_orders': vendor_orders,
          'status_filter': status_filter,
          'vendor': vendor,
      },
  )


@vendor_required
def vendor_order_detail(request, suborder_id):
  vendor = request.user.vendor_profile
  suborder = get_object_or_404(
      VendorOrder.objects.select_related(
          'order__buyer', 'order__shipping_address'
      ).prefetch_related('items'),
      id=suborder_id,
      vendor=vendor,
  )

  if request.method == 'POST':
    new_status = request.POST.get('status')
    courier_name = request.POST.get('courier_name', '')
    tracking_number = request.POST.get('tracking_number', '')

    if new_status in dict(VendorOrder.STATUS_CHOICES):
      suborder.status = new_status
      suborder.courier_name = courier_name
      suborder.tracking_number = tracking_number
      suborder.save()
      messages.success(
          request, f'Fulfillment status for #{suborder.id} updated to {new_status}.'
      )
      return redirect('orders:vendor_order_detail', suborder_id=suborder.id)

  return render(
      request,
      'orders/vendor_order_detail.html',
      {
          'suborder': suborder,
          'status_choices': VendorOrder.STATUS_CHOICES,
      },
  )
