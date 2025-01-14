# orders/models.py
from django.db import models
from cart.models import CartItem, Variant  # Assuming CartItem is in cart app

class Order(models.Model):
    STATUS_CHOICES = [
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]



    order_id = models.CharField(max_length=12, unique=True, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField()
    shipping_method = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new instance (not yet saved)
            super().save(*args, **kwargs)  # Save to get a primary key
            self.order_id = f"ORD{self.pk:08d}"  # Auto-generate order ID
            self.save(update_fields=["order_id"])  # Save the order ID field
        else:
            super().save(*args, **kwargs)


    # def __str__(self):
    #     return f"Order {self.order_id}"

    def calculate_total_bill(self):
        discount_amount = self.total_price * (self.discount / 100)
        tax_amount = self.total_price * (self.tax / 100)
        total_bill = self.total_price - discount_amount + tax_amount
        return total_bill

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    
    # product = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)  # Make sure to link to Variant
    
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item {self.variant.product} in Order {self.order.order_id}"
