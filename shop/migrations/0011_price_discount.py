# Generated by Django 5.0.7 on 2024-10-22 20:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0010_alter_order_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="price",
            name="discount",
            field=models.IntegerField(
                default=0,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
            ),
            preserve_default=False,
        ),
    ]
