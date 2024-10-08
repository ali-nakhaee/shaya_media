# Generated by Django 5.0.7 on 2024-09-02 15:24

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_user_salt"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                blank=True,
                error_messages={"unique": "این نام کاربری قبلا ثبت شده است."},
                help_text="کاراکترهای مجاز: حروف انگلیسی، اعداد و @/./+/-/_",
                max_length=150,
                null=True,
                unique=True,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                verbose_name="username",
            ),
        ),
    ]
