import stripe 
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .cart import Cart
from .serializers import CartItemSerializer, AddToCartSerializer, UpdateCartSerializer
from .forms import CheckoutForm
from .serializers import CheckoutSerializer

# from apps.order.utilities import checkout, notify_customer, notify_vendor

from product.models import Product  # Make sure to import the Product model

class CartDetailView(APIView):
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        # Get the cart
        cart = Cart(request)
        
        # Add the product to the cart
        cart.add(product_id, quantity)

        # Retrieve the product details
        product = Product.objects.get(id=product_id)

        # Prepare the response data
        cart_details = {
            'product_id': product.id,
            'name': product.name,
            'quantity': quantity,
            'price': product.price,
            'total_price': product.price * quantity
        }

        # Return the response with cart details
        return Response({
            'message': 'Product added to cart successfully',
            'cart': cart_details,
            'total_cost': cart.get_total_cost()
        })


def cart_detail(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            stripe.api_key = settings.STRIPE_SECRET_KEY

            stripe_token = form.cleaned_data['stripe_token']

            try:
                charge = stripe.Charge.create(
                    amount=int(cart.get_total_cost() * 100),
                    currency='USD',
                    description='Charge from Interiorshop',
                    source=stripe_token
                )

                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']
                address = form.cleaned_data['address']
                zipcode = form.cleaned_data['zipcode']
                place = form.cleaned_data['place']

                order = checkout(request, first_name, last_name, email, address, zipcode, place, phone, cart.get_total_cost())

                cart.clear()

                notify_customer(order)
                notify_vendor(order)

                return redirect('success')
            except Exception:
                messages.error(request, 'There was something wrong with the payment')
    else:
        form = CheckoutForm()

    remove_from_cart = request.GET.get('remove_from_cart', '')
    change_quantity = request.GET.get('change_quantity', '')
    quantity = request.GET.get('quantity', 0)

    if remove_from_cart:
        cart.remove(remove_from_cart)

        return redirect('cart')
    
    if change_quantity:
        cart.add(change_quantity, quantity, True)

        return redirect('cart')

    return render(request, 'cart/cart.html', {'form': form, 'stripe_pub_key': settings.STRIPE_PUB_KEY})

def success(request):
    return render(request, 'cart/success.html')

class CartAPIView(APIView):
    def get(self, request):
        cart = Cart(request)
        cart_data = [
            {
                'product_id': item['product'].id,
                'quantity': item['quantity'],
                'total_price': item['total_price']
            }
            for item in cart
        ]
        return Response(cart_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            cart = Cart(request)
            cart.add(serializer.validated_data['product_id'], serializer.validated_data['quantity'])
            return Response({'message': 'Product added to cart'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = UpdateCartSerializer(data=request.data)
        if serializer.is_valid():
            cart = Cart(request)
            cart.add(serializer.validated_data['product_id'], serializer.validated_data['quantity'], update_quantity=True)
            return Response({'message': 'Cart updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        product_id = request.data.get('product_id')
        if product_id:
            cart = Cart(request)
            cart.remove(product_id)
            return Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
        return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)


class CheckoutAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [AllowAny]

    def post(self, request):
        cart = Cart(request)
        data = request.data

        # Authenticate user
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        user = authenticate_checkout_user(email, password, first_name, last_name)
        request.user = user  # Log in the user

        cart.merge()  # Merge session cart to user's cart
        serializer = CheckoutSerializer(data=request.data)

        if serializer.is_valid():
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_token = serializer.validated_data['stripe_token']

            try:
                charge = stripe.Charge.create(
                    amount=int(cart.get_total_cost() * 100),
                    currency='USD',
                    description='Charge from Interiorshop',
                    source=stripe_token
                )

            except stripe.error.CardError as e:
                return Response({'error': f"Card Error: {e.user_message}"}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.RateLimitError as e:
                return Response({'error': 'Rate limit error'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            except stripe.error.InvalidRequestError as e:
                return Response({'error': f"Invalid request: {e.user_message}"}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.AuthenticationError as e:
                return Response({'error': 'Authentication error'}, status=status.HTTP_403_FORBIDDEN)
            except stripe.error.APIConnectionError as e:
                return Response({'error': 'Network communication error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except stripe.error.StripeError as e:
                return Response({'error': 'Internal error with Stripe. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


                order = checkout(
                    request,
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data.get('password'),
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    address=serializer.validated_data['address'],
                    zipcode=serializer.validated_data['zipcode'],
                    place=serializer.validated_data['place'],
                    phone=serializer.validated_data['phone'],
                    total_cost=cart.get_total_cost(),
                )

                cart.clear()
                notify_customer(order)
                notify_vendor(order)

                return Response({'message': 'Order successfully placed'}, status=status.HTTP_201_CREATED)

            except stripe.error.StripeError:
                return Response({'error': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def authenticate_checkout_user(email, password, first_name, last_name):
    """Authenticate or register a user."""
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
    return user