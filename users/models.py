""" users.models file """

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator

class User(AbstractUser):
    """ custom user model """
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            # "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
            "کاراکترهای مجاز: حروف انگلیسی، اعداد و @/./+/-/_"
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
