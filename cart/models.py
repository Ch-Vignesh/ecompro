from django.contrib.auth.models import User
from django.db import models
from ecomapp.models import Product, Variant

# class CartItem(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)

#     def __str__(self):
#         return f"{self.product.name} - {self.quantity}"

#     @property
#     def total_price(self):
#         return self.product.price * self.quantity

class Cart(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, default  = None, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)  # You might have a variant for the product
    quantity = models.PositiveIntegerField()

    def get_total_price(self):
        return self.product.price * self.quantity  # Assuming price is in Product
