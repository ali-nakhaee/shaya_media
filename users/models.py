""" users.models file """

import random
import hashlib
import string
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone


class User(AbstractUser):
    """ custom user model """
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        null=True,
        blank=True,
        unique=True,
        help_text=_(
            # "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
            "کاراکترهای مجاز: حروف انگلیسی، اعداد و @/./+/-/_"
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("این نام کاربری قبلا ثبت شده است."),
        },
    )

    password = models.CharField(max_length=200, null=True, blank=True)

    phone_number = models.CharField(max_length=30, unique=True,
                                    error_messages={"unique":"اکانت دیگری با این شماره وجود دارد.",
                                                    },
                                    )
    temporary_password = models.CharField(max_length=200)
    password_generation_time = models.DateTimeField(default=timezone.now)
    salt = models.CharField(max_length=50)

    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)

    receive_email = models.BooleanField(default=True)
    receive_sms = models.BooleanField(default=True)

    is_admin = models.BooleanField(default=False)
    admin_description = models.CharField(max_length=100, blank=True, null=True, default=None)   # A short description of the customer that is only shown to the admin.

    VIEWER = "VIEWER"
    BLOGGER = "BLOGGER"
    ROLE_CHOICES = (
        (VIEWER, "بازدیدکننده"),
        (BLOGGER, "وبلاگ‌نویس"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=VIEWER)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.role == self.VIEWER:
            group, created = Group.objects.get_or_create(name='viewers')
            group.user_set.add(self)
        elif self.role == self.BLOGGER:
            group, created = Group.objects.get_or_create(name='bloggers')
            group.user_set.add(self)

    def __str__(self):
        return self.phone_number
    
    def make_temporary_password(self):
        random_number = random.randint(1000, 9999)
        salt = ''.join(random.choices(string.ascii_letters, k=10))
        hash_object = hashlib.sha256((str(random_number) + salt).encode('utf-8'))  
        hex_dig = hash_object.hexdigest()
        self.temporary_password = hex_dig
        self.salt = salt
        self.password_generation_time = timezone.now()
        self.save()
        return random_number
    
    def check_temporary_password(self, form_password):
        hash_object = hashlib.sha256((str(form_password) + self.salt).encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        delta_time = (datetime.now().astimezone() - self.password_generation_time).total_seconds()
        if (self.temporary_password == hex_dig) and (delta_time < 120):     # Check password and its generation time
            return True
        else:
            return False
