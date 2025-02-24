# Generated by Django 5.0.7 on 2025-02-23 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_alter_user_first_name_alter_user_last_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="receive_email",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="receive_sms",
            field=models.BooleanField(default=True),
        ),
    ]
