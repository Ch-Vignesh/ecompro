from django.shortcuts import render, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Product, Vendor, Order, OrderItem, Cart, CartItem, Review, Notification
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 10  # Optional: Paginate products for better UI

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return Product.objects.filter(name__icontains=query) if query else Product.objects.all()


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

from django.http import HttpResponseForbidden

class VendorDashboardView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'vendor_dashboard.html'
    context_object_name = 'products'

    def get_queryset(self):
        if not hasattr(self.request.user, 'vendor_profile'):
            return HttpResponseForbidden("You are not authorized to view this page.")
        return Product.objects.filter(vendor=self.request.user.vendor_profile)

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'description', 'price', 'inventory', 'category', 'image']
    template_name = 'product_form.html'
    success_url = reverse_lazy('vendor-dashboard')

    def form_valid(self, form):
        form.instance.vendor = self.request.user.vendor_profile
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'price', 'inventory', 'category', 'image']
    template_name = 'product_form.html'
    success_url = reverse_lazy('vendor-dashboard')


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('vendor-dashboard')

class CartDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        context['cart_items'] = CartItem.objects.filter(cart=cart)
        return context


class AddToCartView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        product = Product.objects.get(pk=kwargs['pk'])
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
        cart_item.save()
        return redirect('cart-detail')

class RemoveFromCartView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        cart_item = CartItem.objects.get(pk=kwargs['pk'])
        cart_item.delete()
        return redirect('cart-detail')

class OrderCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'order_confirm.html'

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        order = Order.objects.create(customer=request.user)

        for item in cart.items.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            item.product.inventory -= item.quantity
            item.product.save()
        
        cart.items.all().delete()  # Empty the cart after placing an order
        Notification.objects.create(user=request.user, message="Your order has been placed!")
        return redirect('order-list')


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

class AddReviewView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'comment']
    template_name = 'review_form.html'

    def form_valid(self, form):
        form.instance.customer = self.request.user
        form.instance.product = Product.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('product-detail', kwargs={'pk': self.kwargs['pk']})


class VendorRegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = '/home/wac/Downloads/fullecommerce/ecompro/core/templates/vendor_register.html'
    success_url = reverse_lazy('vendor-dashboard')

    def form_valid(self, form):
        user = form.save()
        user.is_vendor = True  # Add this custom flag
        user.save()
        Vendor.objects.create(user=user, store_name=self.request.POST.get('store_name'))
        login(self.request, user)
        return HttpResponseRedirect(self.success_url)


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
