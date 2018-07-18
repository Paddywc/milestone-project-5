from django import forms
from .models import Suggestion, Comment, SuggestionAdminPage
from accounts.models import User

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        exclude = ["date_time"]
        widgets = {"user": forms.HiddenInput()} #value set in views
    
class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        exclude = ["date_time"]
        widgets = {"user": forms.HiddenInput(), "suggestion": forms.HiddenInput(), "admin_page_comment": forms.HiddenInput()}
        
        

class SuggestionAdminPageForm(forms.ModelForm):
    
    # init function code from:https://stackoverflow.com/questions/291945/how-do-i-filter-foreignkey-choices-in-a-django-modelform
    def __init__(self, *args, **kwargs):
        super(SuggestionAdminPageForm, self).__init__(*args, **kwargs)
        self.fields["developer_assigned"].queryset = User.objects.filter(is_staff=True)

    class Meta:
        model = SuggestionAdminPage
        exclude = ["was_successful", "current_winner", "date_completed"]
        widgets = {"suggestion": forms.HiddenInput(), "date_started": forms.SelectDateWidget(),
        "expected_completion_date": forms.SelectDateWidget(), "estimated_days_to_complete": forms.NumberInput()}


    