from django import forms

from accounts.models import User
from .models import Suggestion, Comment, SuggestionAdminPage


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        exclude = ["date_time"]
        widgets = {"user": forms.HiddenInput()}  # value set in views
        labels = {
            "is_feature": "Suggestion Type",
            "delay_submission": "Delay Submission Till Next Voting Cycle<br> If you're worried that you won't be able to catch up with the current leaders"
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ["date_time"]
        widgets = {"user": forms.HiddenInput(), "suggestion": forms.HiddenInput(),
                   "admin_page_comment": forms.HiddenInput()}


class SuggestionAdminPageForm(forms.ModelForm):

    # init function code from:https://stackoverflow.com/questions/291945/how-do-i-filter-foreignkey-choices-in-a-django-modelform
    # So that only staff can be assigned to a suggestion
    def __init__(self, *args, **kwargs):
        super(SuggestionAdminPageForm, self).__init__(*args, **kwargs)
        self.fields["developer_assigned"].queryset = User.objects.filter(is_staff=True)

    class Meta:
        model = SuggestionAdminPage
        exclude = ["was_successful", "current_winner", "date_completed"]
        widgets = {"suggestion": forms.HiddenInput(), "date_started": forms.SelectDateWidget(),
                   "expected_completion_date": forms.SelectDateWidget(),
                   "estimated_days_to_complete": forms.NumberInput()}
