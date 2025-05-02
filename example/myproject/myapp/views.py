from django.shortcuts import render, redirect, get_object_or_404
from django.utils import translation
from django.utils.translation import gettext as _
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.conf import settings

from .models import Product
from .forms import ProductForm

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Product created successfully!'))
        return super().form_valid(form)

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    
    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('Product updated successfully!'))
        return super().form_valid(form)