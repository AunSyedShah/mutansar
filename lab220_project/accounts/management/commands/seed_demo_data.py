from decimal import Decimal
from accounts.models import Address, User
from django.core.management.base import BaseCommand
from products.models import Category, Product
from vendors.models import Vendor


class Command(BaseCommand):
  help = 'Seeds initial demonstration data for Admin, Vendors, Buyer, Categories, and Products.'

  def handle(self, *args, **options):
    self.stdout.write(self.style.NOTICE('Seeding demo data...'))

    # 1. Superadmin User
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@multimarket.com',
            'is_staff': True,
            'is_superuser': True,
            'is_buyer': True,
            'is_vendor': False,
        },
    )
    if created:
      admin_user.set_password('admin123')
      admin_user.save()
      self.stdout.write(
          self.style.SUCCESS('Created Superadmin: admin / admin123')
      )

    # 2. Buyer User
    buyer_user, created = User.objects.get_or_create(
        username='buyer1',
        defaults={
            'email': 'buyer@example.com',
            'phone_number': '+92 300 1112233',
            'is_buyer': True,
            'is_vendor': False,
        },
    )
    if created:
      buyer_user.set_password('buyer123')
      buyer_user.save()
      Address.objects.create(
          user=buyer_user,
          full_name='Ali Khan',
          phone='+92 300 1112233',
          street_address='House 42, Street 10, Sector F-7/2',
          city='Islamabad',
          state='Federal',
          postal_code='44000',
          country='Pakistan',
          is_default=True,
      )
      self.stdout.write(self.style.SUCCESS('Created Buyer: buyer1 / buyer123'))

    # 3. Vendor 1 (TechZone)
    v1_user, created = User.objects.get_or_create(
        username='seller1',
        defaults={
            'email': 'contact@techzone.com',
            'phone_number': '+92 301 5556677',
            'is_buyer': False,
            'is_vendor': True,
        },
    )
    if created:
      v1_user.set_password('seller123')
      v1_user.save()
      vendor1 = Vendor.objects.create(
          user=v1_user,
          store_name='TechZone Electronics',
          description=(
              'Official seller of premium wireless audio, mechanical keyboards,'
              ' and smart peripherals.'
          ),
          commission_rate=Decimal('10.00'),
          bank_name='Meezan Bank',
          bank_account_title='TechZone Pvt Ltd',
          bank_account_number='010203040506',
          is_approved=True,
          is_active=True,
      )
      self.stdout.write(
          self.style.SUCCESS(
              'Created Vendor 1: seller1 / seller123 (TechZone Electronics)'
          )
      )
    else:
      vendor1 = v1_user.vendor_profile

    # 4. Vendor 2 (Nordic Home)
    v2_user, created = User.objects.get_or_create(
        username='seller2',
        defaults={
            'email': 'hello@nordichome.com',
            'phone_number': '+92 302 8889900',
            'is_buyer': False,
            'is_vendor': True,
        },
    )
    if created:
      v2_user.set_password('seller123')
      v2_user.save()
      vendor2 = Vendor.objects.create(
          user=v2_user,
          store_name='Nordic Home & Living',
          description=(
              'Handcrafted Scandinavian ceramics, minimalist ambient lighting,'
              ' and sustainable decor.'
          ),
          commission_rate=Decimal('10.00'),
          bank_name='Habib Bank Limited',
          bank_account_title='Nordic Living Studio',
          bank_account_number='998877665544',
          is_approved=True,
          is_active=True,
      )
      self.stdout.write(
          self.style.SUCCESS(
              'Created Vendor 2: seller2 / seller123 (Nordic Home & Living)'
          )
      )
    else:
      vendor2 = v2_user.vendor_profile

    # 5. Categories
    cat_tech, _ = Category.objects.get_or_create(
        name='Electronics & Gadgets', defaults={'slug': 'electronics-gadgets'}
    )
    cat_home, _ = Category.objects.get_or_create(
        name='Home & Living', defaults={'slug': 'home-living'}
    )
    cat_fashion, _ = Category.objects.get_or_create(
        name='Fashion & Apparel', defaults={'slug': 'fashion-apparel'}
    )

    # 6. Products for Vendor 1 (TechZone)
    p1, _ = Product.objects.get_or_create(
        vendor=vendor1,
        title='Pro Wireless Noise-Cancelling Headphones',
        defaults={
            'category': cat_tech,
            'description': (
                'Experience immersive 40mm acoustic drivers, 35-hour battery'
                ' life, and hybrid active noise cancellation.'
            ),
            'price': Decimal('199.99'),
            'discount_price': Decimal('169.99'),
            'stock': 25,
            'is_active': True,
            'is_featured': True,
        },
    )
    p2, _ = Product.objects.get_or_create(
        vendor=vendor1,
        title='Compact RGB Mechanical Keyboard (Cherry Red)',
        defaults={
            'category': cat_tech,
            'description': (
                'Smooth linear switches, hot-swappable PCB, and PBT double-shot'
                ' keycaps with custom per-key backlighting.'
            ),
            'price': Decimal('89.99'),
            'discount_price': None,
            'stock': 40,
            'is_active': True,
            'is_featured': True,
        },
    )

    # 7. Products for Vendor 2 (Nordic Home)
    p3, _ = Product.objects.get_or_create(
        vendor=vendor2,
        title='Handcrafted Matte Ceramic Mug Set (4-Pack)',
        defaults={
            'category': cat_home,
            'description': (
                'Artisan stoneware finished in warm earth glazes. Microwave and'
                ' dishwasher safe for everyday coffee lovers.'
            ),
            'price': Decimal('38.00'),
            'discount_price': Decimal('32.00'),
            'stock': 15,
            'is_active': True,
            'is_featured': True,
        },
    )
    p4, _ = Product.objects.get_or_create(
        vendor=vendor2,
        title='Minimalist Dimmable LED Desk Lamp',
        defaults={
            'category': cat_home,
            'description': (
                'Brushed aluminum body with touch-sensitive dimming, 3 color'
                ' temperature modes, and wireless phone charging pad.'
            ),
            'price': Decimal('49.50'),
            'discount_price': None,
            'stock': 20,
            'is_active': True,
            'is_featured': False,
        },
    )

    self.stdout.write(
        self.style.SUCCESS('Successfully seeded multi-vendor database!')
    )
    self.stdout.write("""
Test Credentials:
--------------------------------------------------
[Superadmin]: username = admin   | password = admin123
[Seller 1]:   username = seller1 | password = seller123  (TechZone Electronics)
[Seller 2]:   username = seller2 | password = seller123  (Nordic Home & Living)
[Buyer]:      username = buyer1  | password = buyer123
--------------------------------------------------
""")
