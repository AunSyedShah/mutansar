from django import forms
from .models import Payout, Vendor


class VendorProfileForm(forms.ModelForm):

  class Meta:
    model = Vendor
    fields = (
        'store_name',
        'description',
        'logo',
        'banner',
        'bank_account_title',
        'bank_name',
        'bank_account_number',
        'bank_iban',
    )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for name, field in self.fields.items():
      if name in ['logo', 'banner']:
        field.widget.attrs.update({
            'class': (
                'w-full text-xs text-slate-500 file:mr-3 file:py-1.5'
                ' file:px-3 file:rounded-lg file:border-0 file:text-xs'
                ' file:font-semibold file:bg-brand-50 file:text-brand-700'
                ' hover:file:bg-brand-100'
            )
        })
      else:
        field.widget.attrs.update({
            'class': (
                'w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm'
                ' focus:ring-2 focus:ring-brand-500 focus:border-brand-500'
                ' outline-none'
            )
        })


class PayoutRequestForm(forms.ModelForm):

  class Meta:
    model = Payout
    fields = ('amount',)
    widgets = {
        'amount': forms.NumberInput(
            attrs={
                'class': (
                    'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                    ' text-sm focus:ring-2 focus:ring-brand-500'
                    ' focus:border-brand-500 outline-none'
                ),
                'placeholder': '50.00',
                'min': '10.00',
                'step': '0.01',
            }
        ),
    }
