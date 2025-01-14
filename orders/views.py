# orders/views.py
from rest_framework import status, generics
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import CartItem
from cart.serializers import CartItemSerializer
import random
from rest_framework.views import APIView
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import NotFound
import razorpay

import string
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404

class OrderCreateAPIView(APIView):
    def post(self, request, cart_id):
        # Fetch cart items
        cart_items = CartItem.objects.filter(cart_id=cart_id)
        if not cart_items.exists():
            return Response({"error": "Cart is empty or invalid cart ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize cart items
        serialized_items = CartItemSerializer(cart_items, many=True)
        # Calculate subtotal from serialized data
        subtotal = sum(item['total_price'] for item in serialized_items.data)

        # Convert constants to Decimal for calculations
        discount_rate = Decimal("0.06")  # 6%
        tax_rate = Decimal("0.18")  # 18%

        # Calculate discount and tax
        discount = (subtotal * discount_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        tax = ((subtotal - discount) * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_price = (subtotal - discount + tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Create the order
        order_data = {
            "name": request.data.get("name"),
            "email": request.data.get("email"),
            "address": request.data.get("address"),
            "shipping_method": request.data.get("shipping_method"),
            "payment_method": request.data.get("payment_method"),
            "total_price": total_price,
            "discount": discount,
            "tax": tax,
        }
        serializer = OrderSerializer(data=order_data)
        if serializer.is_valid():
            order = serializer.save()

            # Create OrderItems using only Variant
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,  # Use only the variant
                    
                    quantity=item.quantity,
                    price=item.variant.price  # Use the variant price
                )
                

            # payment_url = f"http://127.0.0.1:8000/payments/order/{order.id}/initiate/"
            # return redirect(payment_url)
                

            self.send_order_email(order)


            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_order_email(self, order):
        subject = f"Order Confirmation: {order.order_id}"
        order_items = OrderItem.objects.filter(order=order)

        item_details = ""
        for item in order_items:
            item_details += f"Product: {item.variant.product}\nVariant:{item.variant} \nQuantity: {item.quantity}\nPrice: {item.price} each\n\n"
    
    # Build the message with order and item details
        message = f"""Dear {order.name},

    Your order {order.order_id} has been placed successfully.

Order Details:
Total Price: {order.total_price}
Discount: {order.discount}
Tax: {order.tax}

Shipping Method: {order.shipping_method}
Payment Method: {order.payment_method}
Status: {order.status}

Items:
{item_details}

Thank you for shopping with us! We will notify you once your order is shipped.
"""


        # message = f"Dear {order.name},\n\nYour order {order.order_id} has been placed successfully.\nTotal Price: {order.calculate_total_bill()}\n\nThank you for shopping with us!"
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # Sender email
                [order.email],  # Recipient email
                fail_silently=False,  # False to raise errors
            )
            print(f"Email sent to {order.email}")
        except Exception as e:
            print(f"Error sending email: {str(e)}")


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        # Fetch cart items for user (replace this logic based on your cart integration)
        cart_items = CartItem.objects.all()  # Modify as per your cart logic
        
        # for item in cart_items:
        #     item_varient = item.variant.price
        #     item_quantity = item.quantity
        
        total_price = sum([item.variant.price * item.quantity for item in cart_items])
        
        # total_price = sum([item_varient * item_quantity])

        # Generate Order ID
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        order = serializer.save(order_id=order_id, total_price=total_price)

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item, quantity=item.quantity, price=item.variant.price)

        # Send email to customer
        self.send_order_email(order)

    def send_order_email(self, order):
        subject = f"Order Confirmation: {order.order_id}"
        message = f"Dear {order.name},\n\nYour order {order.order_id} has been placed successfully.\nTotal Price: {order.calculate_total_bill()}\n\nThank you for shopping with us!"
        
        try:

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # your email address
                [order.email],
                fail_silently=False,
            )
            print(f"Email sent to {order.email}")
        except Exception as e:
            print(f"Error sending email: {str(e)}")




class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


@api_view(['PATCH'])
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    status = request.data.get('status', order.status)
    order.status = status
    order.save()

    return Response({'detail': 'Order status updated successfully'})


class OrderDetailAPIView(RetrieveAPIView):
    serializer_class = OrderSerializer
    lookup_field = 'id'  # Default is 'pk', but you can specify the field
    
    def get_queryset(self):
        return Order.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        order_id = self.kwargs.get('order_id')
        try:
            return queryset.get(id=order_id)
        except Order.DoesNotExist:
            raise NotFound({'error': f"Order with ID {order_id} does not exist"})

    def put(self, request, *args, **kwargs):
        order = self.get_object()
        # Use the serializer to validate and update the order data
        serializer = self.get_serializer(order, data=request.data, partial=False)  # partial=False for PUT method
        if serializer.is_valid():
            # Save the updated order
            updated_order = serializer.save()

            # Send email to notify about the update
            self.send_order_email(updated_order)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_order_email(self, order):
        subject = f"Order Updated: {order.order_id}"
        message = f"Dear {order.name},\n\nYour order {order.order_id} has been updated successfully.\n\nUpdated Details:\nTotal Price: {order.total_price}\nDiscount: {order.discount}\nTax: {order.tax}\nShipping Method: {order.shipping_method}\nPayment Method: {order.payment_method}\nStatus: {order.status}\nThank you for shopping with us!"
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # your email address
                [order.email],
                fail_silently=False,
            )
            print(f"Email sent to {order.email}")
        except Exception as e:
            print(f"Error sending email: {str(e)}")


# Reorder functionality

class ReorderAPIView(APIView):
    def post(self, request, order_id):
        try:
            # Fetch the original order by order_id
            original_order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate a new order ID
        new_order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Prepare order data by copying details from the original order
        order_data = {
            "name": original_order.name,
            "email": original_order.email,
            "address": original_order.address,
            "shipping_method": original_order.shipping_method,
            "payment_method": original_order.payment_method,
            "total_price": original_order.total_price,
            "discount": original_order.discount,
            "tax": original_order.tax,
            "order_id": new_order_id,  # new order ID
        }

        # Serialize the new order data
        serializer = OrderSerializer(data=order_data)
        if serializer.is_valid():
            # Save the new order
            new_order = serializer.save()

            # Copy the order items from the original order
            for item in original_order.items.all():
                OrderItem.objects.create(
                    order=new_order,
                    variant=item.variant,
                    quantity=item.quantity,
                    price=item.price
                )

            # Send email notification for the new order
            self.send_order_email(new_order)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_order_email(self, order):
        subject = f"Order Confirmation: {order.order_id} (Reorder)"
        message = f"Dear {order.name},\n\nYour reorder {order.order_id} has been placed successfully.\n\nOrder Details:\nTotal Price: {order.total_price}\nDiscount: {order.discount}\nTax: {order.tax}\nShipping Method: {order.shipping_method}\nPayment Method: {order.payment_method}\n\nThank you for shopping with us!"
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # your email address
                [order.email],
                fail_silently=False,
            )
            print(f"Email sent to {order.email}")
        except Exception as e:
            print(f"Error sending email: {str(e)}")

