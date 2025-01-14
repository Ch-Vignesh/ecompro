from django.urls import path
from .views import CartAPIView, CheckoutAPIView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CartListCreateAPIView, AddCartItemAPIView, CartDetailAPIView


from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart'),
    path('success/', views.success, name='success'),
    path('api/cart/', CartAPIView.as_view(), name='cart-api'),
    path('api/checkout/', CheckoutAPIView.as_view(), name='checkout-api'),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('<int:product_id>/remove/', views.CartItemDeleteView.as_view(), name='cart_item_remove'),
    # Add a product to the cart
    path('<int:product_id>/add/', views.CartAddItemView.as_view(), name='cart_item_add'),
    # Remove a product from the cart
    path('<int:product_id>/remove/', views.CartAddItemView.as_view(), name='cart_item_remove'),
    path('view/', views.CartView.as_view(), name='view_cart'),
    
    # new cart urls
    path('carts/', CartListCreateAPIView.as_view(), name='cart-list-create'),
    path('carts/<int:cart_id>/add-item/', AddCartItemAPIView.as_view(), name='add-cart-item'),
    path('carts/<int:pk>/', CartDetailAPIView.as_view(), name='cart-detail'),

]