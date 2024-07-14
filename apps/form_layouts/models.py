from django.db import models
from apps.authentication.models import cafe

class Regular_customer(models.Model):
    cafe = models.ForeignKey(cafe, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.IntegerField()

    def __str__(self):
        return self.name

class Bill_regular(models.Model):
    cafe = models.ForeignKey(cafe, on_delete=models.CASCADE)
    customer = models.ForeignKey(Regular_customer, on_delete=models.CASCADE)
    total = models.FloatField()
    reaming = models.FloatField()
    date = models.DateField()
    items = models.JSONField()

    def __str__(self):
        return self.customer.name

class Account_balance(models.Model):
    cafe = models.ForeignKey(cafe, on_delete=models.CASCADE)
    customer = models.ForeignKey(Regular_customer, on_delete=models.CASCADE)
    bills = models.ManyToManyField(Bill_regular)
    complete = models.BooleanField()

    def __str__(self):
        return self.customer.name
