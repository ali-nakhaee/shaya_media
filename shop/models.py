from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Type(models.Model):
    type = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class Subject(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    subject = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.type.type} - {self.subject}"


class Level(models.Model):
    level_num = models.IntegerField(unique=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Price(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    min_range = models.IntegerField()   # Minimum value for this price range based on Type.unit
    max_range = models.IntegerField()   # Maximum value for this price range based on Type.unit
    price = models.IntegerField()

    def __str__(self):
        return str(self.price)


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.PROTECT)
    purchase_date = models.DateTimeField(default=timezone.now)


class Item(models.Model):
    """ Each item in cart """
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    number = models.IntegerField()
    item_price = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    def save(self, *args, **kwargs):
        self.item_price = Price.objects.get(type=self.type, subject=self.subject, level=self.level).price * self.number
        super().save(*args, **kwargs)
