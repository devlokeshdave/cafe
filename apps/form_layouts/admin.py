from django.contrib import admin
from .models import Regular_customer, Bill_regular, Account_balance
# Register your models here.

admin.site.register(Regular_customer)
admin.site.register(Bill_regular)
admin.site.register(Account_balance)
