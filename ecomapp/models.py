# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
# Product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    seller = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True) 
    
    def __str__(self):
        return self.name
    


# Attribute model (e.g., Color, Size)
class Attribute(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# Value model (e.g., Red, Medium)
class Value(models.Model):
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=255)
    

    def __str__(self):
        return self.value

# ProductAttribute model to associate products with attributes and values
class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, related_name='attributes', on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, related_name='product_attributes', on_delete=models.CASCADE)
    value = models.ForeignKey(Value, related_name='product_attributes', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.name} - {self.attribute.name} - {self.value.value}'


class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # Rating from 1 to 5
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name} - {self.rating} Stars"





class Reply(models.Model):
    review = models.ForeignKey(Review, related_name="replies", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username}"
    
    

#variants for each products
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    attributes = models.ManyToManyField(Value, related_name="variants")  # Links values to this variant
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Optional SKU for the variant
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)  # Stock quantity
    status = models.CharField(max_length=20, choices=[('in_stock', 'In Stock'), ('out_of_stock', 'Out of Stock')], default='in_stock')

    def is_in_stock(self):
        return self.stock > 0
    
    def __str__(self):
        return f" {self.product.name} - {self.sku}"
    
class VariantImage(models.Model):
    variant = models.ForeignKey(Variant, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='variants/%Y/%m/%d/')
    is_main_image = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.variant.sku}"