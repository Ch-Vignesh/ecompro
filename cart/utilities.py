from django.contrib.auth.models import User
from apps.order.models import Order

def checkout(request, email, password, first_name, last_name, address, zipcode, place, phone, total_cost):
    if not request.user.is_authenticated:
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        request.user = user

    order = Order.objects.create(
        user=request.user,
        address=address,
        zipcode=zipcode,
        place=place,
        phone=phone,
        total_cost=total_cost,
    )
    return order
