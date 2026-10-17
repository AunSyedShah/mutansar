from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Vendor(models.Model):
    """Storefront & Business profile for approved sellers."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_profile'
    )
    store_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='vendors/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='vendors/banners/', blank=True, null=True)

    # Platform governance
    is_approved = models.BooleanField(
        default=False,
        help_text="Superadmin approval required before store goes live."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Can be suspended or disabled by Superadmin."
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text="Platform fee percentage (e.g. 10.00 for 10%)"
    )

    # Bank/Payout details
    bank_account_title = models.CharField(max_length=150, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_iban = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.store_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.store_name


class Payout(models.Model):
  """Tracks payout disbursements from Platform Owner to Vendor."""

  STATUS_CHOICES = (
      ('pending', 'Pending'),
      ('approved', 'Approved'),
      ('paid', 'Paid'),
      ('rejected', 'Rejected'),
  )

  vendor = models.ForeignKey(
      Vendor, on_delete=models.CASCADE, related_name='payouts'
  )
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  status = models.CharField(
      max_length=20, choices=STATUS_CHOICES, default='pending'
  )
  transaction_reference = models.CharField(
      max_length=100,
      blank=True,
      help_text='Bank transfer or payment reference ID',
  )
  admin_note = models.TextField(blank=True)
  requested_at = models.DateTimeField(auto_now_add=True)
  processed_at = models.DateTimeField(blank=True, null=True)

  class Meta:
    ordering = ['-requested_at']

  def __str__(self):
    return (
        f'Payout #{self.id} - {self.vendor.store_name} - ${self.amount}'
        f' ({self.status})'
    )
