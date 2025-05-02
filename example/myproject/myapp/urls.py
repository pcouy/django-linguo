from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path("i18n/", include("django.conf.urls.i18n")),
] 