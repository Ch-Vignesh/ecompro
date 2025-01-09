from django.conf import settings

from product.models import Product
from django.contrib.auth.models import User
from .models import CartItem


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        self.user = request.user if request.user.is_authenticated else None
        self.cart = self.session.get(settings.CART_SESSION_ID, {})

    def add(self, product_id, quantity=1, update_quantity=False):
        product = Product.objects.get(id=product_id)
        
        if self.user:
            cart_item, created = CartItem.objects.get_or_create(user=self.user, product=product)
            if update_quantity:
                cart_item.quantity += int(quantity)
            else:
                cart_item.quantity = int(quantity)
            cart_item.save()
        else:
            product_id = str(product_id)
            if product_id not in self.cart:
                self.cart[product_id] = {'quantity': 0, 'id': product_id}
            if update_quantity:
                self.cart[product_id]['quantity'] += int(quantity)
            else:
                self.cart[product_id]['quantity'] = int(quantity)
            self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def merge(self):
        """Merge session cart into user's cart."""
        if not self.user:
            return

        for product_id, item in self.cart.items():
            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(user=self.user, product=product)
            cart_item.quantity += item['quantity']
            cart_item.save()

        self.clear()

    def clear(self):
        """Clear session cart."""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product
        for item in self.cart.values():
            item['total_price'] = item['product'].price * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_cost(self):
        return sum(item['product'].price * item['quantity'] for item in self)

    def merge_cart_with_user(self, user):
        # Merge session cart with user's saved cart
        pass  # Implementation coming soon
