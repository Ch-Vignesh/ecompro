from django.urls import path
from .views import CartAPIView, CheckoutAPIView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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

]