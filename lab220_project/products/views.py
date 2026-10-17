from accounts.decorators import buyer_required, vendor_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from vendors.models import Vendor
from .forms import ProductForm, ProductImageForm, ReviewForm
from .models import Category, Product, ProductImage, Review


def home_view(request):
  """Marketplace landing page featuring categories, top sellers, and spotlight items."""
  featured_products = (
      Product.objects.filter(
          is_active=True, is_featured=True, vendor__is_approved=True, vendor__is_active=True
      )
      .select_related('vendor')
      .prefetch_related('images')[:8]
  )
  latest_products = (
      Product.objects.filter(
          is_active=True, vendor__is_approved=True, vendor__is_active=True
      )
      .select_related('vendor')
      .prefetch_related('images')
      .order_by('-created_at')[:8]
  )
  categories = Category.objects.filter(parent__isnull=True)[:8]
  vendors = Vendor.objects.filter(is_approved=True, is_active=True)[:6]

  return render(
      request,
      'home.html',
      {
          'featured_products': featured_products,
          'latest_products': latest_products,
          'categories': categories,
          'vendors': vendors,
      },
  )


def product_list_view(request):
  """Public catalog view with multi-faceted search, category, and sorting filters."""
  products = (
      Product.objects.filter(
          is_active=True,
          vendor__is_approved=True,
          vendor__is_active=True,
      )
      .select_related('vendor', 'category')
      .prefetch_related('images')
  )

  # Text search
  query = request.GET.get('q', '').strip()
  if query:
    products = products.filter(
        Q(title__icontains=query)
        | Q(description__icontains=query)
        | Q(vendor__store_name__icontains=query)
    )

  # Category filter
  category_slug = request.GET.get('category')
  selected_category = None
  if category_slug:
    selected_category = get_object_or_404(Category, slug=category_slug)
    products = products.filter(
        Q(category=selected_category)
        | Q(category__parent=selected_category)
    )

  # Price range filter
  min_price = request.GET.get('min_price')
  max_price = request.GET.get('max_price')
  if min_price:
    products = products.filter(price__gte=min_price)
  if max_price:
    products = products.filter(price__lte=max_price)

  # Sorting
  sort = request.GET.get('sort', 'newest')
  if sort == 'price_low':
    products = products.order_by('price')
  elif sort == 'price_high':
    products = products.order_by('-price')
  else:
    products = products.order_by('-created_at')

  paginator = Paginator(products, 12)
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)

  categories = Category.objects.filter(parent__isnull=True)

  return render(
      request,
      'products/product_list.html',
      {
          'page_obj': page_obj,
          'categories': categories,
          'selected_category': selected_category,
          'query': query,
          'sort': sort,
      },
  )


def product_detail_view(request, slug):
  product = get_object_or_404(
      Product.objects.select_related('vendor', 'category').prefetch_related(
          'images', 'reviews__buyer'
      ),
      slug=slug,
      is_active=True,
  )

  reviews = product.reviews.all()
  avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
  user_has_reviewed = False
  if request.user.is_authenticated:
    user_has_reviewed = reviews.filter(buyer=request.user).exists()

  review_form = ReviewForm()

  # Related products from same vendor or category
  related_products = (
      Product.objects.filter(category=product.category, is_active=True)
      .exclude(id=product.id)
      .select_related('vendor')[:4]
  )

  return render(
      request,
      'products/product_detail.html',
      {
          'product': product,
          'reviews': reviews,
          'avg_rating': round(avg_rating, 1) if avg_rating else None,
          'user_has_reviewed': user_has_reviewed,
          'review_form': review_form,
          'related_products': related_products,
      },
  )


def vendor_storefront_view(request, slug):
  vendor = get_object_or_404(Vendor, slug=slug, is_approved=True, is_active=True)
  products = (
      Product.objects.filter(vendor=vendor, is_active=True)
      .select_related('category')
      .prefetch_related('images')
  )

  return render(
      request,
      'products/vendor_storefront.html',
      {
          'vendor': vendor,
          'products': products,
      },
  )


@buyer_required
def add_product_review(request, slug):
  product = get_object_or_404(Product, slug=slug, is_active=True)

  if Review.objects.filter(product=product, buyer=request.user).exists():
    messages.warning(request, 'You have already reviewed this product.')
    return redirect('products:detail', slug=slug)

  if request.method == 'POST':
    form = ReviewForm(request.POST)
    if form.is_valid():
      review = form.save(commit=False)
      review.product = product
      review.buyer = request.user
      review.save()
      messages.success(request, 'Your review was posted!')
    else:
      messages.error(request, 'Failed to post review. Please check inputs.')

  return redirect('products:detail', slug=slug)


# ==========================================
# VENDOR PRODUCT CATALOG MANAGEMENT (PORTAL)
# ==========================================


@vendor_required
def vendor_products_list(request):
  vendor = request.user.vendor_profile
  products = (
      Product.objects.filter(vendor=vendor)
      .select_related('category')
      .prefetch_related('images')
  )

  return render(
      request,
      'products/vendor_product_list.html',
      {
          'products': products,
          'vendor': vendor,
      },
  )


@vendor_required
def vendor_product_create(request):
  vendor = request.user.vendor_profile

  if request.method == 'POST':
    form = ProductForm(request.POST)
    img_form = ProductImageForm(request.POST, request.FILES)
    if form.is_valid() and img_form.is_valid():
      product = form.save(commit=False)
      product.vendor = vendor
      product.save()

      if request.FILES.get('image'):
        product_image = img_form.save(commit=False)
        product_image.product = product
        product_image.is_primary = True
        product_image.save()

      messages.success(
          request, f'Product "{product.title}" created successfully!'
      )
      return redirect('products:vendor_products')
  else:
    form = ProductForm()
    img_form = ProductImageForm()

  return render(
      request,
      'products/vendor_product_form.html',
      {
          'form': form,
          'img_form': img_form,
          'action_title': 'Add New Product',
      },
  )


@vendor_required
def vendor_product_edit(request, product_id):
  vendor = request.user.vendor_profile
  product = get_object_or_404(Product, id=product_id, vendor=vendor)

  if request.method == 'POST':
    form = ProductForm(request.POST, instance=product)
    img_form = ProductImageForm(request.POST, request.FILES)
    if form.is_valid() and img_form.is_valid():
      form.save()
      if request.FILES.get('image'):
        product_image = img_form.save(commit=False)
        product_image.product = product
        product_image.save()

      messages.success(request, f'Product "{product.title}" updated.')
      return redirect('products:vendor_products')
  else:
    form = ProductForm(instance=product)
    img_form = ProductImageForm()

  return render(
      request,
      'products/vendor_product_form.html',
      {
          'form': form,
          'img_form': img_form,
          'product': product,
          'action_title': f'Edit {product.title}',
      },
  )


@vendor_required
def vendor_product_delete(request, product_id):
  vendor = request.user.vendor_profile
  product = get_object_or_404(Product, id=product_id, vendor=vendor)

  if request.method == 'POST':
    product.delete()
    messages.success(request, 'Product deleted from your catalog.')
  return redirect('products:vendor_products')
