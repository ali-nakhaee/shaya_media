# Generated by Django 5.0.7 on 2024-09-05 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0009_alter_order_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.SmallIntegerField(
                choices=[
                    (0, "در حال بررسی"),
                    (1, "پذیرفته شده"),
                    (2, "در حال انجام"),
                    (3, "به اتمام رسیده"),
                    (4, "رد شده"),
                ],
                default=0,
            ),
        ),
    ]
