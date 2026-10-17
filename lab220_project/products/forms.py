from django import forms
from .models import Category, Product, ProductImage, Review


class ProductForm(forms.ModelForm):

  class Meta:
    model = Product
    fields = (
        'title',
        'category',
        'price',
        'discount_price',
        'stock',
        'description',
        'is_active',
        'is_featured',
    )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for name, field in self.fields.items():
      if name in ['is_active', 'is_featured']:
        field.widget.attrs.update({
            'class': (
                'h-4 w-4 rounded border-slate-300 text-brand-600'
                ' focus:ring-brand-500'
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


class ProductImageForm(forms.ModelForm):

  class Meta:
    model = ProductImage
    fields = ('image', 'alt_text', 'is_primary')

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['image'].widget.attrs.update({
        'class': (
            'w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3'
            ' file:rounded-lg file:border-0 file:text-xs file:font-semibold'
            ' file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100'
        )
    })
    self.fields['alt_text'].widget.attrs.update({
        'class': (
            'w-full px-3 py-1.5 rounded-lg border border-slate-300 text-xs'
            ' focus:ring-2 focus:ring-brand-500 outline-none'
        ),
        'placeholder': 'Image alt description',
    })
    self.fields['is_primary'].widget.attrs.update({
        'class': (
            'h-4 w-4 rounded border-slate-300 text-brand-600'
            ' focus:ring-brand-500'
        )
    })


class ReviewForm(forms.ModelForm):

  class Meta:
    model = Review
    fields = ('rating', 'comment')
    widgets = {
        'rating': forms.Select(
            choices=[
                (5, '5 Stars - Outstanding'),
                (4, '4 Stars - Very Good'),
                (3, '3 Stars - Average'),
                (2, '2 Stars - Poor'),
                (1, '1 Star - Very Bad'),
            ],
            attrs={
                'class': (
                    'w-full px-3.5 py-2 rounded-lg border border-slate-300'
                    ' text-sm focus:ring-2 focus:ring-brand-500 outline-none'
                )
            },
        ),
        'comment': forms.Textarea(
            attrs={
                'class': (
                    'w-full px-3.5 py-2 rounded-lg border border-slate-300'
                    ' text-sm focus:ring-2 focus:ring-brand-500 outline-none'
                ),
                'rows': 3,
                'placeholder': (
                    'Share your genuine experience with this item...'
                ),
            }
        ),
    }
