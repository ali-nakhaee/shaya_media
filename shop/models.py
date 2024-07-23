from django.db import models


class Type(models.Model):
    type = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class Subject(models.Model):
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.type.type} - {self.subject}"


class Level(models.Model):
    level_num = models.IntegerField(unique=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Price(models.Model):
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    min_range = models.IntegerField()   # Minimum value for this price range based on Type.unit
    max_range = models.IntegerField()   # Maximum value for this price range based on Type.unit
    price = models.IntegerField()

    def __str__(self):
        return str(self.price)

