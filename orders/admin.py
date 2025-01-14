# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'name', 'email', 'status', 'total_price', 'created_at']
    list_filter = ['status']
    search_fields = ['order_id', 'name', 'email']

admin.site.register(OrderItem)
