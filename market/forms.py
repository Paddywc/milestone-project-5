from django import forms
from .models import Delivery

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        exclude = ["date"]
        widgets = {"user": forms.HiddenInput()} #value set in views
    
