
# Create your models here.
from django.db import models
from apps.authentication.models import cafe

class Menu(models.Model):
    cafe = models.ForeignKey(cafe, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.FloatField()
    date = models.DateField(null=True)
    qty = models.FloatField(default=0)
    pieces_qty = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    discount = models.FloatField(default=0)
    total_pieces = models.IntegerField(default=1)
    category = models.CharField(max_length=100, default="Beverages")
    
    def __str__(self):
        return self.name
    
    
class Number_table(models.Model):
    cafe = models.ForeignKey(cafe, on_delete=models.CASCADE, null=True)
    number = models.IntegerField()
    
    def __str__(self):
        return str(self.number)
    
    

class Order_list(models.Model):
    cafe = models.ForeignKey(cafe, on_delete=models.CASCADE, null=True)
    name = models.CharField(null=True, max_length=50, blank=True)
    table = models.CharField(max_length=50)
    date = models.DateField()
    items = models.JSONField()
    tax = models.FloatField()
    discount = models.FloatField(blank=True, null=True)
    total = models.FloatField()
    
    def __str__(self):
        return self.table
    

class tax(models.Model):
    cafe = models.ForeignKey(cafe, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    tax = models.FloatField()
    
    def __str__(self):
        return self.name
    