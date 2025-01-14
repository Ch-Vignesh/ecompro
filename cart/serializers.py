from rest_framework import serializers
from .models import Cart, CartItem, Product, Variant

from ecomapp.models import Product, Variant

# class CartItemSerializer(serializers.Serializer):
#     product_id = serializers.IntegerField()
#     quantity = serializers.IntegerField(min_value=1)

# class CartSerializer(serializers.Serializer):
#     items = CartItemSerializer(many=True)

#     def validate_items(self, items):
#         for item in items:
#             try:
#                 Product.objects.get(pk=item['product_id'])
#             except Product.DoesNotExist:
#                 raise serializers.ValidationError(f"Product with ID {item['product_id']} does not exist.")
#         return items

#     total_price = serializers.FloatField()

# class AddToCartSerializer(serializers.Serializer):
#     product_id = serializers.IntegerField()
#     quantity = serializers.IntegerField(default=1)

# class UpdateCartSerializer(serializers.Serializer):
#     product_id = serializers.IntegerField()
#     quantity = serializers.IntegerField()


# new methods for the cart app

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    variant = serializers.PrimaryKeyRelatedField(queryset=Variant.objects.all())  # Handle variant
    quantity = serializers.IntegerField()
    total_price = serializers.SerializerMethodField()  # Add a new field for total price

    class Meta:
        model = CartItem
        fields = ['product', 'variant', 'quantity', 'total_price']

    def get_total_price(self, obj):
        price = obj.variant.price
        if price is None:
            return 0  # or some other default value, depending on your use case
        return price * obj.quantity


    # class Meta:
    #     model = CartItem
    #     fields = ['product', 'variant', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)  # 'items' as a list of cart items

    class Meta:
        model = Cart
        fields = [ 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        cart = Cart.objects.create(**validated_data)
        for item_data in items_data:
            CartItem.objects.create(cart=cart, **item_data)
        return cart


# order serializer(checkout)
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
