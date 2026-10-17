from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from vendors.models import Vendor
from .models import Address

User = get_user_model()


class BuyerRegistrationForm(UserCreationForm):
  email = forms.EmailField(
      required=True,
      widget=forms.EmailInput(
          attrs={
              'class': (
                  'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                  ' text-sm focus:ring-2 focus:ring-brand-500'
                  ' focus:border-brand-500 outline-none'
              ),
              'placeholder': 'you@example.com',
          }
      ),
  )
  phone_number = forms.CharField(
      required=False,
      widget=forms.TextInput(
          attrs={
              'class': (
                  'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                  ' text-sm focus:ring-2 focus:ring-brand-500'
                  ' focus:border-brand-500 outline-none'
              ),
              'placeholder': '+92 300 1234567',
          }
      ),
  )

  class Meta:
    model = User
    fields = ('username', 'email', 'phone_number')

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field_name in self.fields:
      self.fields[field_name].widget.attrs.update({
          'class': (
              'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm'
              ' focus:ring-2 focus:ring-brand-500 focus:border-brand-500'
              ' outline-none'
          )
      })

  def save(self, commit=True):
    user = super().save(commit=False)
    user.is_buyer = True
    user.is_vendor = False
    if commit:
      user.save()
    return user


class VendorRegistrationForm(UserCreationForm):
  email = forms.EmailField(
      required=True,
      widget=forms.EmailInput(
          attrs={
              'class': (
                  'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                  ' text-sm focus:ring-2 focus:ring-brand-500'
                  ' focus:border-brand-500 outline-none'
              ),
              'placeholder': 'business@store.com',
          }
      ),
  )
  phone_number = forms.CharField(
      required=True,
      widget=forms.TextInput(
          attrs={
              'class': (
                  'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                  ' text-sm focus:ring-2 focus:ring-brand-500'
                  ' focus:border-brand-500 outline-none'
              ),
              'placeholder': '+92 300 7654321',
          }
      ),
  )
  store_name = forms.CharField(
      max_length=200,
      required=True,
      widget=forms.TextInput(
          attrs={
              'class': (
                  'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                  ' text-sm focus:ring-2 focus:ring-brand-500'
                  ' focus:border-brand-500 outline-none'
              ),
              'placeholder': 'Apex Gadgets & Tech',
          }
      ),
  )
  store_description = forms.CharField(
      required=False,
      widget=forms.Textarea(
          attrs={
              'class': (
                  'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                  ' text-sm focus:ring-2 focus:ring-brand-500'
                  ' focus:border-brand-500 outline-none'
              ),
              'rows': 3,
              'placeholder': 'Tell buyers what your store sells...',
          }
      ),
  )
  bank_name = forms.CharField(
      max_length=100,
      required=False,
      widget=forms.TextInput(
          attrs={
              'class': (
                  'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                  ' text-sm focus:ring-2 focus:ring-brand-500'
                  ' focus:border-brand-500 outline-none'
              ),
              'placeholder': 'Meezan Bank / HBL',
          }
      ),
  )
  bank_account_number = forms.CharField(
      max_length=50,
      required=False,
      widget=forms.TextInput(
          attrs={
              'class': (
                  'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                  ' text-sm focus:ring-2 focus:ring-brand-500'
                  ' focus:border-brand-500 outline-none'
              ),
              'placeholder': '1234567890',
          }
      ),
  )

  class Meta:
    model = User
    fields = (
        'username',
        'email',
        'phone_number',
        'store_name',
        'store_description',
        'bank_name',
        'bank_account_number',
    )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field_name in self.fields:
      self.fields[field_name].widget.attrs.update({
          'class': (
              'w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm'
              ' focus:ring-2 focus:ring-brand-500 focus:border-brand-500'
              ' outline-none'
          )
      })

  def clean_store_name(self):
    store_name = self.cleaned_data.get('store_name')
    if Vendor.objects.filter(store_name__iexact=store_name).exists():
      raise forms.ValidationError(
          'A store with this name already exists. Please pick another name.'
      )
    return store_name

  def save(self, commit=True):
    user = super().save(commit=False)
    user.is_vendor = True
    user.is_buyer = False
    if commit:
      user.save()
      Vendor.objects.create(
          user=user,
          store_name=self.cleaned_data['store_name'],
          description=self.cleaned_data.get('store_description', ''),
          bank_name=self.cleaned_data.get('bank_name', ''),
          bank_account_number=self.cleaned_data.get('bank_account_number', ''),
          is_approved=False,  # Needs admin approval
      )
    return user


class AddressForm(forms.ModelForm):

  class Meta:
    model = Address
    fields = (
        'full_name',
        'phone',
        'street_address',
        'apartment',
        'city',
        'state',
        'postal_code',
        'country',
        'is_default',
    )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for name, field in self.fields.items():
      if name == 'is_default':
        field.widget.attrs.update({
            'class': (
                'h-4 w-4 rounded border-slate-300 text-brand-600'
                ' focus:ring-brand-500'
            )
        })
      else:
        field.widget.attrs.update({
            'class': (
                'w-full px-3.5 py-2.5 rounded-lg border border-slate-300'
                ' text-sm focus:ring-2 focus:ring-brand-500'
                ' focus:border-brand-500 outline-none'
            )
        })
