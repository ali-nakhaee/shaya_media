# Generated by Django 5.0.7 on 2024-08-28 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_user_password_generation_time_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="salt",
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
