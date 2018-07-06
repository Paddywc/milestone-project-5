from django import forms
from .models import Suggestion
from tinymce.widgets import TinyMCE

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        exclude = ["date_time"]
        widgets = {"user": forms.HiddenInput(), "details":TinyMCE(attrs={'cols': 80, 'rows': 30})} #value set in views
    
