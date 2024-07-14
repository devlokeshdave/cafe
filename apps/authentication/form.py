from django.forms import ModelForm
from .models import permission, cafe

class updateCafe(ModelForm):
    class Meta:
        model = cafe
        fields = ["name","contact_no","city","state","address"]
        
    
