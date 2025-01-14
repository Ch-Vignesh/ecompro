from django.conf import settings

from ecomapp.models import Product
from django.contrib.auth.models import User
from .models import CartItem


class Cart(object):
    def __init__(self, request):
        """Initialize the cart with the current session"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            # If cart doesn't exist, initialize it as an empty dictionary
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def __iter__(self):
        """Iterate through all the items in the cart and get product details"""
        for product_id in self.cart:
            self.cart[product_id]['product'] = Product.objects.get(pk=product_id)

        for item in self.cart.values():
            item['total_price'] = item['product'].price * item['quantity']
            yield item

    def __len__(self):
        """Return the total number of items in the cart"""
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product_id, quantity=1, update_quantity=False):
        """Add a product to the cart"""
        product_id = str(product_id)  # Ensure product_id is a string (can be a number in DB)

        if product_id not in self.cart:
            # If the product is not in the cart, add it with a quantity
            self.cart[product_id] = {'quantity': 0, 'id': product_id}

        if update_quantity:
            self.cart[product_id]['quantity'] += int(quantity)
        else:
            self.cart[product_id]['quantity'] = int(quantity)

        # Ensure quantity does not go below 0
        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product_id)

        self.save()

    def remove(self, product_id):
        """Remove a product from the cart"""
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """Save the cart in the session"""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        """Clear the cart"""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_total_cost(self):
        """Calculate the total cost of all products in the cart"""
        total = sum(item['quantity'] * item['product'].price for item in self.cart.values())
        return total

    def merge(self):
        # """Merge session cart into user's cart."""
        # if not self.user:
        #     return

        # for product_id, item in self.cart.items():
        #     product = Product.objects.get(id=product_id)
        #     cart_item, created = CartItem.objects.get_or_create(user=self.user, product=product)
        #     cart_item.quantity += item['quantity']
        #     cart_item.save()

        # self.clear()
        pass  # Implementation coming soon


    def merge_cart_with_user(self, user):
        # Merge session cart with user's saved cart
        pass  # Implementation coming soon
