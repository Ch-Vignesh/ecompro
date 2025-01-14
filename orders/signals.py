from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from django.core.mail import send_mail

@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    if created:
        subject = f"Order Confirmation - {instance.order_id}"
        message = f"Thank you for your order, {instance.name}!\n\nOrder Details:\nOrder ID: {instance.order_id}\nTotal: {instance.total_price}\n\nAddress: {instance.address}\n\nWe will notify you once your order is shipped."
        
        try:
            send_mail(
                subject,
                message,
                'vigneschinthakuntla4666@gmail.com',  # Sender's email
                [instance.email],  # Recipient's email
                fail_silently=False,  # False to get detailed errors
            )
            print(f"Order confirmation email sent to {instance.email}")
        except Exception as e:
            print(f"Error sending email: {str(e)}")
