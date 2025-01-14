# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import CartItem

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=CartItem.objects.all())
    
    class Meta:
        model = OrderItem
        fields = ['product','variant', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['order_id', 'name', 'email', 'address', 'shipping_method', 'payment_method', 'status', 'items', 'total_price', 'discount', 'tax']

    def get_items(self, obj):
    # Fetch order items associated with the order
        order_items = OrderItem.objects.filter(order=obj)
        return [{
            "product": item.variant.product.id,
            "variant": item.variant.id,
            "quantity": item.quantity,
            "price": item.price,  # Variant price
        } for item in order_items]
