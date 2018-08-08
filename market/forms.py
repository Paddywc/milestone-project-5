from django import forms

from .models import Delivery


class DeliveryForm(forms.ModelForm):
    """
    Date excluded as it auto adds today. User
    is hidden as it is specified as request.user when
    creating the form in views.py
    """
    class Meta:
        model = Delivery
        exclude = ["date", "current_delivery_method"]
        widgets = {"user": forms.HiddenInput()}  # value set in views
