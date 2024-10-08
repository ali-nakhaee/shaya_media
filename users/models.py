""" users.models file """

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

    password = models.CharField(max_length=20, null=True, blank=True)

    phone_number = models.CharField(max_length=30, unique=True)
    temporary_password = models.CharField(max_length=200)
    password_generation_time = models.DateTimeField(default=timezone.now)
    salt = models.CharField(max_length=50)

    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)

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
            