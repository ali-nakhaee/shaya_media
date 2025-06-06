# Generated by Django 5.0.7 on 2025-03-16 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0014_order_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="ordered_by_admin",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="order",
            name="description",
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
    ]
