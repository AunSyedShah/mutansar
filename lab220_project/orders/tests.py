from decimal import Decimal
from accounts.models import Address, User
from django.test import Client, TestCase
from products.models import Category, Product
from vendors.models import Vendor
from .models import Cart, CartItem, Order, OrderItem, VendorOrder


class MultiVendorOrderSplittingTest(TestCase):

  def setUp(self):
    self.client = Client()

    # Create Buyer
    self.buyer = User.objects.create_user(
        username='testbuyer', password='password123', is_buyer=True
    )
    self.address = Address.objects.create(
        user=self.buyer,
        full_name='Test Buyer',
        phone='1234567890',
        street_address='123 Market St',
        city='Lahore',
        state='Punjab',
        postal_code='54000',
        country='Pakistan',
        is_default=True,
    )

    # Create Vendor 1
    self.v1_user = User.objects.create_user(
        username='vendor_one', password='password123', is_vendor=True
    )
    self.vendor1 = Vendor.objects.create(
        user=self.v1_user,
        store_name='Store Alpha',
        commission_rate=Decimal('10.00'),
        is_approved=True,
        is_active=True,
    )

    # Create Vendor 2
    self.v2_user = User.objects.create_user(
        username='vendor_two', password='password123', is_vendor=True
    )
    self.vendor2 = Vendor.objects.create(
        user=self.v2_user,
        store_name='Store Beta',
        commission_rate=Decimal('15.00'),
        is_approved=True,
        is_active=True,
    )

    self.category = Category.objects.create(name='Tech', slug='tech')

    # Products
    self.prod1 = Product.objects.create(
        vendor=self.vendor1,
        category=self.category,
        title='Alpha Item 1',
        price=Decimal('100.00'),
        stock=10,
        is_active=True,
    )
    self.prod2 = Product.objects.create(
        vendor=self.vendor2,
        category=self.category,
        title='Beta Item 1',
        price=Decimal('50.00'),
        stock=5,
        is_active=True,
    )

  def test_multi_vendor_checkout_splits_orders(self):
    """Test that checking out with items from Store Alpha and Store Beta creates 1 parent Order and 2 VendorOrders with correct commissions."""
    self.client.login(username='testbuyer', password='password123')

    # 1. Add both products to cart
    cart = Cart.objects.create(user=self.buyer)
    CartItem.objects.create(cart=cart, product=self.prod1, quantity=1)  # $100
    CartItem.objects.create(cart=cart, product=self.prod2, quantity=2)  # $100

    self.assertEqual(cart.total_price, Decimal('200.00'))

    # 2. Place Order via Checkout
    response = self.client.post(
        '/orders/checkout/',
        {'address_id': self.address.id, 'payment_method': 'cod'},
    )
    self.assertEqual(response.status_code, 302)

    # 3. Verify Master Order
    self.assertEqual(Order.objects.count(), 1)
    master_order = Order.objects.first()
    self.assertEqual(master_order.total_amount, Decimal('200.00'))
    self.assertEqual(master_order.buyer, self.buyer)

    # 4. Verify VendorOrder Splits
    vendor_orders = master_order.vendor_orders.all()
    self.assertEqual(vendor_orders.count(), 2)

    # Store Alpha Sub-Order check
    sub_alpha = vendor_orders.get(vendor=self.vendor1)
    self.assertEqual(sub_alpha.subtotal, Decimal('100.00'))
    self.assertEqual(sub_alpha.commission_fee, Decimal('10.00'))  # 10% of $100
    self.assertEqual(sub_alpha.vendor_earnings, Decimal('90.00'))
    self.assertEqual(sub_alpha.items.count(), 1)

    # Store Beta Sub-Order check
    sub_beta = vendor_orders.get(vendor=self.vendor2)
    self.assertEqual(sub_beta.subtotal, Decimal('100.00'))
    self.assertEqual(sub_beta.commission_fee, Decimal('15.00'))  # 15% of $100
    self.assertEqual(sub_beta.vendor_earnings, Decimal('85.00'))
    self.assertEqual(sub_beta.items.count(), 1)

    # 5. Verify Inventory Stock Reduction
    self.prod1.refresh_from_db()
    self.prod2.refresh_from_db()
    self.assertEqual(self.prod1.stock, 9)
    self.assertEqual(self.prod2.stock, 3)

    # 6. Verify Cart Emptied
    self.assertEqual(cart.items.count(), 0)
