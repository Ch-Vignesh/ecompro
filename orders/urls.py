# orders/urls.py
from django.urls import path
from .views import OrderCreateView, OrderListView,OrderDetailAPIView
from .views import OrderCreateAPIView, ReorderAPIView


urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('', OrderListView.as_view(), name='order-list'),
    path('carts/<int:cart_id>/order/', OrderCreateAPIView.as_view(), name='create-order'),
    path('<int:order_id>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/', OrderDetailAPIView.as_view(), name='order-detail-update'),
    path('orders/reorder/<str:order_id>/', ReorderAPIView.as_view(), name='reorder'),

]
