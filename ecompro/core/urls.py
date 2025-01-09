from django.urls import path
from .views import (
    ProductListView, ProductDetailView, VendorDashboardView, ProductCreateView, 
    ProductUpdateView, ProductDeleteView, CartDetailView, AddToCartView, 
    RemoveFromCartView, OrderCreateView, OrderListView, AddReviewView, 
    VendorRegistrationView, NotificationListView
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('vendor/dashboard/', VendorDashboardView.as_view(), name='vendor-dashboard'),
    path('vendor/register/', VendorRegistrationView.as_view(), name='vendor-register'),
    path('product/add/', ProductCreateView.as_view(), name='product-add'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product-edit'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/<int:pk>/', AddToCartView.as_view(), name='cart-add'),
    path('cart/remove/<int:pk>/', RemoveFromCartView.as_view(), name='cart-remove'),
    path('order/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('product/<int:pk>/review/', AddReviewView.as_view(), name='add-review'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
]
