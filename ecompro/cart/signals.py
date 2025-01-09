from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .cart import Cart

@receiver(user_logged_in)
def merge_cart(sender, request, user, **kwargs):
    cart = Cart(request)
    cart.merge()
