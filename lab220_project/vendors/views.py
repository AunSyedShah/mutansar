from decimal import Decimal
from accounts.decorators import vendor_required
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render
from orders.models import VendorOrder
from products.models import Product
from .forms import PayoutRequestForm, VendorProfileForm
from .models import Payout


@vendor_required
def vendor_dashboard(request):
  vendor = request.user.vendor_profile

  # Metrics
  vendor_orders = VendorOrder.objects.filter(vendor=vendor)
  total_sales = (
      vendor_orders.aggregate(Sum('subtotal'))['subtotal__sum'] or Decimal('0.00')
  )
  commission_paid = (
      vendor_orders.aggregate(Sum('commission_fee'))['commission_fee__sum']
      or Decimal('0.00')
  )
  net_earnings = (
      vendor_orders.aggregate(Sum('vendor_earnings'))['vendor_earnings__sum']
      or Decimal('0.00')
  )

  pending_orders_count = vendor_orders.filter(status='pending').count()
  total_products_count = Product.objects.filter(vendor=vendor).count()

  recent_orders = vendor_orders.select_related(
      'order__buyer', 'order__shipping_address'
  ).order_by('-created_at')[:5]

  return render(
      request,
      'vendors/dashboard.html',
      {
          'vendor': vendor,
          'total_sales': total_sales,
          'commission_paid': commission_paid,
          'net_earnings': net_earnings,
          'pending_orders_count': pending_orders_count,
          'total_products_count': total_products_count,
          'recent_orders': recent_orders,
      },
  )


@vendor_required
def vendor_settings(request):
  vendor = request.user.vendor_profile

  if request.method == 'POST':
    form = VendorProfileForm(request.POST, request.FILES, instance=vendor)
    if form.is_valid():
      form.save()
      messages.success(request, 'Store profile & banking details updated.')
      return redirect('vendors:settings')
  else:
    form = VendorProfileForm(instance=vendor)

  return render(
      request,
      'vendors/settings.html',
      {
          'form': form,
          'vendor': vendor,
      },
  )


@vendor_required
def vendor_payouts(request):
  vendor = request.user.vendor_profile

  # Total earnings across delivered orders
  delivered_earnings = (
      VendorOrder.objects.filter(vendor=vendor, status='delivered').aggregate(
          Sum('vendor_earnings')
      )['vendor_earnings__sum']
      or Decimal('0.00')
  )

  # Total payouts already processed or pending
  total_withdrawn_or_pending = (
      Payout.objects.filter(
          vendor=vendor, status__in=['pending', 'approved', 'paid']
      ).aggregate(Sum('amount'))['amount__sum']
      or Decimal('0.00')
  )

  available_balance = max(
      Decimal('0.00'), delivered_earnings - total_withdrawn_or_pending
  )

  payouts = Payout.objects.filter(vendor=vendor)

  if request.method == 'POST':
    form = PayoutRequestForm(request.POST)
    if form.is_valid():
      requested_amount = form.cleaned_data['amount']
      if requested_amount > available_balance:
        messages.error(
            request,
            f'Requested amount (${requested_amount}) exceeds your available'
            f' balance (${available_balance}).',
        )
      elif requested_amount < Decimal('10.00'):
        messages.error(request, 'Minimum withdrawal amount is $10.00.')
      else:
        payout = form.save(commit=False)
        payout.vendor = vendor
        payout.status = 'pending'
        payout.save()
        messages.success(
            request,
            f'Payout request for ${requested_amount} submitted to'
            ' administrator.',
        )
        return redirect('vendors:payouts')
  else:
    form = PayoutRequestForm()

  return render(
      request,
      'vendors/payouts.html',
      {
          'vendor': vendor,
          'delivered_earnings': delivered_earnings,
          'available_balance': available_balance,
          'payouts': payouts,
          'form': form,
      },
  )
