from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Order

User = get_user_model()

@receiver(post_save, sender=Order)
def send_email_to_admin(sender, instance, created, **kwargs):
    """ Function for sending alert email to admin after customer make a new order. """
    """if created:
        subject = "سفارش جدید"
        message = "سلام. سفارش جدیدی در سایت ثبت شده است."
        admin_emails = list(User.objects.filter(is_admin=True).values_list('email', flat=True))
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            admin_emails,
            fail_silently=False,
        )
        print(f"emial sent to {admin_emails}")"""
