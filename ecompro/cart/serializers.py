from rest_framework import serializers
from product.models import Product

class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    total_price = serializers.FloatField()

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

class UpdateCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

class CheckoutSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    address = serializers.CharField()
    zipcode = serializers.CharField()
    place = serializers.CharField()
    phone = serializers.CharField()
    stripe_token = serializers.CharField()
