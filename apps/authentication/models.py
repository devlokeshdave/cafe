
# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class cafe(models.Model):
    name = models.CharField(max_length=50, unique=True)
    contact_no = models.IntegerField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    address = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name 
    

class permission(models.Model):
    cafe = models.ForeignKey(cafe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        name = f"{self.cafe.name} {self.user.first_name}"
        return name

    