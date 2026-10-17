from products.models import Category
from .models import Cart


def ecommerce_context(request):
  """Provides global cart item count and product categories to all templates."""
  cart_count = 0
  if request.user.is_authenticated:
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
      cart_count = cart.total_items
  elif request.session.session_key:
    cart = Cart.objects.filter(session_key=request.session.session_key).first()
    if cart:
      cart_count = cart.total_items

  categories = Category.objects.filter(parent__isnull=True)[:8]

  return {
      'global_cart_count': cart_count,
      'global_categories': categories,
  }
