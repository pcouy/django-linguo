from django.db import models
from django.utils.translation import gettext_lazy as _

from linguo.models import MultilingualModel
from linguo.managers import MultilingualManager

class Product(MultilingualModel):
    name = models.CharField(max_length=255, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'))
    price = models.DecimalField(verbose_name=_('price'), max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=100, unique=True, verbose_name=_('SKU'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = MultilingualManager()
    
    class Meta:
        # Define which fields should be translatable
        translate = ('name', 'description')
        
    def __str__(self):
        return self.name 