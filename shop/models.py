from decouple import config

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

User = settings.AUTH_USER_MODEL


class Type(models.Model):
    type = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.type


class Subject(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    subject = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.subject


class Level(models.Model):
    level_num = models.IntegerField(unique=True)
    title = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Price(models.Model):
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    min_range = models.IntegerField()   # Minimum value for this price range based on Type.unit
    max_range = models.IntegerField()   # Maximum value for this price range based on Type.unit
    price = models.IntegerField()
    is_available = models.BooleanField(default=True)
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   default=0,
                                   )

    def __str__(self):
        return str(self.price)


class Order(models.Model):

    class Meta:
        permissions = [
            ("change_order_status", "Can change the status of orders"),
        ]
    buyer = models.ForeignKey(User, on_delete=models.PROTECT)
    purchase_date = models.DateTimeField(default=timezone.now)
    tracking_code = models.IntegerField(null=True)
    price = models.IntegerField()
    description = models.TextField(max_length=300, null=True, blank=True)

    PENDING = 0
    ACCEPTED = 1
    DOING = 2
    FINISHED = 3
    REJECTED = 4
    
    STATUS_CHOICES = (
        (PENDING, "در حال بررسی"),
        (ACCEPTED, "پذیرفته شده"),
        (DOING, "در حال انجام"),
        (FINISHED, "به اتمام رسیده"),
        (REJECTED, "رد شده"),
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    ordered_by_admin = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.tracking_code = 1
        super().save(*args, **kwargs)
        tracking_code = int(str(self.id * int(config('multiplication_value'))), base=int(config('base_value'))) + int(config('addition_value'))
        Order.objects.filter(id=self.id).update(tracking_code=tracking_code)
    
    def get_order_status(self, status_num): # Only for all_orders View. Need to change.
        return self.STATUS_CHOICES[status_num][1]


class Item(models.Model):
    """ Each item in order """
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    number = models.IntegerField()
    item_price = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    # def save(self, *args, **kwargs):
    #     self.item_price = Price.objects.get(type=self.type, subject=self.subject, level=self.level).price * self.number
    #     super().save(*args, **kwargs)
