from django import forms

from .models import Delivery


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        exclude = ["date", "current_delivery_method"]
        widgets = {"user": forms.HiddenInput()}  # value set in views
