from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from .forms import AddressForm, BuyerRegistrationForm, VendorRegistrationForm
from .models import Address


def login_view(request):
  if request.user.is_authenticated:
    if request.user.is_vendor and hasattr(request.user, 'vendor_profile'):
      if request.user.vendor_profile.is_approved:
        return redirect('vendors:dashboard')
      return redirect('accounts:vendor_pending')
    return redirect('home')

  if request.method == 'POST':
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request, user)
      messages.success(request, f'Welcome back, {user.username}!')

      next_url = request.GET.get('next')
      if next_url:
        return redirect(next_url)

      if user.is_staff:
        return redirect('/admin/')
      if user.is_vendor and hasattr(user, 'vendor_profile'):
        if user.vendor_profile.is_approved:
          return redirect('vendors:dashboard')
        return redirect('accounts:vendor_pending')
      return redirect('home')
    else:
      messages.error(request, 'Invalid username or password. Please try again.')
  else:
    form = AuthenticationForm()

  return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
  logout(request)
  messages.info(request, 'You have been signed out successfully.')
  return redirect('home')


def register_buyer(request):
  if request.user.is_authenticated:
    return redirect('home')

  if request.method == 'POST':
    form = BuyerRegistrationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      messages.success(
          request,
          'Account created successfully! Welcome to MultiMarket.',
      )
      return redirect('home')
    else:
      messages.error(
          request, 'Please correct the errors below to register.'
      )
  else:
    form = BuyerRegistrationForm()

  return render(request, 'accounts/register_buyer.html', {'form': form})


def register_vendor(request):
  if request.user.is_authenticated:
    if request.user.is_vendor:
      return redirect('vendors:dashboard')
    messages.warning(
        request, 'You are currently signed in as a buyer. Please sign out first.'
    )
    return redirect('home')

  if request.method == 'POST':
    form = VendorRegistrationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      messages.success(
          request,
          'Vendor application submitted successfully! Your account is pending'
          ' admin review.',
      )
      return redirect('accounts:vendor_pending')
    else:
      messages.error(
          request, 'Please resolve the highlighted errors to submit.'
      )
  else:
    form = VendorRegistrationForm()

  return render(request, 'accounts/register_vendor.html', {'form': form})


def vendor_pending_view(request):
  if not request.user.is_authenticated or not request.user.is_vendor:
    return redirect('home')

  if (
      hasattr(request.user, 'vendor_profile')
      and request.user.vendor_profile.is_approved
  ):
    return redirect('vendors:dashboard')

  return render(request, 'accounts/vendor_pending.html')


@login_required
def addresses_view(request):
  addresses = Address.objects.filter(user=request.user)

  if request.method == 'POST':
    form = AddressForm(request.POST)
    if form.is_valid():
      address = form.save(commit=False)
      address.user = request.user
      if address.is_default or not addresses.exists():
        Address.objects.filter(user=request.user).update(is_default=False)
        address.is_default = True
      address.save()
      messages.success(request, 'Address saved successfully.')
      return redirect('accounts:addresses')
  else:
    form = AddressForm()

  return render(
      request,
      'accounts/addresses.html',
      {'addresses': addresses, 'form': form},
  )


@login_required
def address_delete_view(request, address_id):
  address = get_object_or_404(Address, id=address_id, user=request.user)
  if request.method == 'POST':
    address.delete()
    messages.success(request, 'Address deleted.')
  return redirect('accounts:addresses')
