from django.forms import ModelForm
from .models import Order_list

class Order(ModelForm):
    class Meta:
        model = Order_list
        fields = ["cafe","name","table","date","items","tax","discount","total"]


        
    
