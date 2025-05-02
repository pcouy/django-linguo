from django import forms
from linguo.forms import MultilingualModelForm
from .models import Product

class ProductForm(forms.ModelForm):
    """Regular model form that works in the current language"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'sku']

class ProductAdminForm(MultilingualModelForm):
    """Admin form that allows editing all languages at once"""
    class Meta:
        model = Product
        fields = '__all__' 