# tasks.py

from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task(subject, message, from_email, recipient_list, fail_silently, *args, **kwargs):
    send_mail(subject, message, from_email, recipient_list, fail_silently, *args, **kwargs)
