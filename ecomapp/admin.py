from django.contrib import admin

# Register your models here.
from .models import Product, Attribute, Value, ProductAttribute, Review, Reply, Category, VariantImage, Variant

admin.site.register(Product)
admin.site.register(Attribute)
admin.site.register(Value)
admin.site.register(ProductAttribute)
admin.site.register(Review)
admin.site.register(Reply)
admin.site.register(Category)
admin.site.register(Variant)
admin.site.register(VariantImage)
