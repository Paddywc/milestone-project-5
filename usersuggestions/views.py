from django.shortcuts import render
from .forms import SuggestionForm
from django.contrib.auth.decorators import login_required

@login_required()
def add_suggestion(request):
    """
    """
    # user value hidden using widget
    # therefore set as current user here
    form = SuggestionForm(initial={"user": request.user})
    
    
    return render(request, 'add_suggestion.html', {"form": form})