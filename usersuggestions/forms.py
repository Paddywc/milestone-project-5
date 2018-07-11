from django import forms
from .models import Suggestion, Comment

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        exclude = ["date_time"]
        widgets = {"user": forms.HiddenInput()} #value set in views
    
class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        exclude = ["date_time"]
        widgets = {"user": forms.HiddenInput(), "suggestion": forms.HiddenInput()}