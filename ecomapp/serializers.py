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
        

#for reply        
class ReplySerializer(serializers.ModelSerializer):
    seller_name = serializers.StringRelatedField()  # Display sellername

    class Meta:
        model = Reply
        fields = ['id', 'review', 'seller_name', 'reply', 'created_at']
        
    def get_seller_name(self, obj):
        # Assuming 'user' in the Reply model is the vendor (seller)
        return obj.user.username if obj.user else None

#for reviews
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display username
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'content', 'rating', 'created_at','replies']



class NestedValueSerializer(serializers.ModelSerializer):
    attribute = serializers.CharField(source='attribute.name')  # Display the attribute name
    value = serializers.CharField()  # Display the value

    class Meta:
        model = Value
        fields = ['attribute', 'value']
   
class VariantImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = VariantImage
        fields = ['id', 'image','is_main_image']

    def validate(self, attrs):
        # Ensure only one main image is set for the variant
        is_main_image = attrs.get('is_main_image', False)
        variant = self.context.get('variant')

        if is_main_image and VariantImage.objects.filter(variant=variant, is_main_image=True).exists():
            raise serializers.ValidationError("A main image is already set for this variant.")
        
        return attrs
     
class VariantSerializer(serializers.ModelSerializer):
    images = VariantImageSerializer(many=True, read_only=True)
    attributes = serializers.SerializerMethodField()
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = Variant
        fields = ('id', 'product','sku','images', 'product_image', 'price', 'stock', 'status','attributes')
        
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        variant = Variant.objects.create(**validated_data)

        for image_data in images_data:
            VariantImage.objects.create(variant=variant, **image_data)

        return variant
    
    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        instance = super().update(instance, validated_data)

        for image_data in images_data:
            VariantImage.objects.create(variant=instance, **image_data)
        return instance

    def get_attributes(self, obj):
        # Ensure attributes are fetched correctly
        # Assuming `attributes` is a related name on the Variant model.
        return [
            {value.attribute.name: value.value} for value in obj.attributes.all()
        ]


        

# Detailed product serializer with attributes and values
class ProductDetailSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)  # Include reviews in product details
    variants = VariantSerializer(many=True, required=False)
    category = CategorySerializer()
    attributes = NestedValueSerializer(many=True, required=False)
    average_rating =  serializers.SerializerMethodField()

    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description','brand', 'seller', 'reviews','average_rating', 'category', 'image', 'attributes','variants']


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
    
    def create(self, validated_data):
        # Extract nested data
        category_name = validated_data.pop('category', None)
        variants_data = validated_data.pop('variants', [])
        attributes_data = validated_data.pop('attributes', [])

        # Handle category
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
            validated_data['category'] = category

        # Create the product
        product = Product.objects.create(**validated_data)
        
        for attribute_data in attributes_data:
            attribute_name = attribute_data.get('attribute')
            value = attribute_data.get('value')

            if attribute_name and value:
                attribute, _ = Attribute.objects.get_or_create(name=attribute_name)
                # Find or create a Value for the attribute
                value_obj, _ = Value.objects.get_or_create(attribute=attribute, value=value)
                # Create ProductAttribute to associate attribute and value with the product
                ProductAttribute.objects.create(product=product, attribute=attribute, value=value_obj)


        return product