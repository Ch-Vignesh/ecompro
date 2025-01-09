from django.contrib import admin
from .models import Vendor, Product, Cart, CartItem, Order, OrderItem, Review, Notification

# Vendor Admin
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'created_at')
    search_fields = ('store_name', 'user__username')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'inventory', 'category', 'created_at')
    search_fields = ('name', 'vendor__store_name', 'category')
    list_filter = ('category', 'vendor', 'created_at')
    ordering = ('-created_at',)
    prepopulated_fields = {'category': ('name',)}  # Optional for slug-like behavior

# Cart Admin
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # Prevent additional blank rows

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'cart_identifier', 'created_at')
    search_fields = ('user__username', 'cart_identifier')
    inlines = [CartItemInline]

# Order Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'created_at')
    search_fields = ('customer__username', 'status')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'created_at')
    search_fields = ('product__name', 'customer__username')
    list_filter = ('rating', 'created_at')

# Notification Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read', 'created_at')
    search_fields = ('user__username', 'message')
    list_filter = ('read', 'created_at')
    ordering = ('-created_at',)
