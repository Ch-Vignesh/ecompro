# catalog/serializers.py

from rest_framework import serializers
from .models import Product, Attribute, Value, ProductAttribute, VariantImage, Variant, Reply, Review, Category
from django.db.models import Avg

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id','name']
    
# Attribute serializer
class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']

# Value serializer
class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ['id', 'attribute', 'value']

# ProductAttribute serializer
class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['id', 'product', 'attribute', 'value']
        
#for reviews
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display username

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'content', 'rating', 'created_at']

#for reply        
class ReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display username

    class Meta:
        model = Reply
        fields = ['id', 'review', 'user', 'reply', 'created_at']

# Detailed product serializer with attributes and values
class ProductDetailSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)  # Include reviews in product details
    
    attributes = serializers.SerializerMethodField()
    category = CategorySerializer()
    average_rating =  serializers.SerializerMethodField()

    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description','brand', 'seller', 'reviews','average_rating', 'category', 'attributes']

    def get_attributes(self, obj):
        product_attributes = ProductAttribute.objects.filter(product=obj)
        return [
            {
                "id": pa.attribute.id,
                "attribute": pa.attribute.name,
                "value": pa.value.value
            }
            for pa in product_attributes
        ]
        
    def get_average_rating(self, obj):
        avg_rating = obj.reviews.aggregate(average=Avg('rating'))['average']
        return avg_rating if avg_rating else 0

class NestedValueSerializer(serializers.ModelSerializer):
    attribute = serializers.CharField(source='attribute.name')  # Display the attribute name
    value = serializers.CharField()  # Display the value

    class Meta:
        model = Value
        fields = ['attribute', 'value']
   
class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = ['id', 'image']

     
class VariantSerializer(serializers.ModelSerializer):
    image = VariantImageSerializer(many=True, read_only=True)
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = ('id', 'product','sku','image', 'price', 'stock', 'status','attributes')

    def get_attributes(self, obj):
        # Ensure attributes are fetched correctly
        # Assuming `attributes` is a related name on the Variant model.
        return [
            {value.attribute.name: value.value} for value in obj.attributes.all()
        ]

class ProductSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True)
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = ['id', 'name', 'description','seller', 'brand','category', 'image','variants']
        
        

