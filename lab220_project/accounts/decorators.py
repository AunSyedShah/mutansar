from functools import wraps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def vendor_required(view_func):
  """Decorator to ensure the authenticated user is an approved vendor."""

  @wraps(view_func)
  def _wrapped_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
      messages.info(request, 'Please log in to access the vendor portal.')
      return redirect('accounts:login')

    if not request.user.is_vendor or not hasattr(
        request.user, 'vendor_profile'
    ):
      messages.warning(
          request, 'Access restricted. Vendor account required.'
      )
      return redirect('home')

    if not request.user.vendor_profile.is_approved:
      messages.warning(
          request,
          'Your vendor account is pending approval by the platform'
          ' administrator.',
      )
      return redirect('accounts:vendor_pending')

    if not request.user.vendor_profile.is_active:
      messages.error(
          request,
          'Your vendor account has been deactivated. Please contact support.',
      )
      return redirect('home')

    return view_func(request, *args, **kwargs)

  return _wrapped_view


def buyer_required(view_func):
  """Decorator to ensure the authenticated user is a buyer."""

  @wraps(view_func)
  def _wrapped_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
      messages.info(request, 'Please log in to continue.')
      return redirect('accounts:login')
    return view_func(request, *args, **kwargs)

  return _wrapped_view
