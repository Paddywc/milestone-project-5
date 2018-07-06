from django.shortcuts import render
from .forms import SuggestionForm
from django.contrib.auth.decorators import login_required
from django.conf import settings

@login_required()
def add_suggestion(request):
    """
    """
    if (settings.COINS_ENABLED):
        print("This is running")
    # user value hidden using widget
    # therefore set as current user here
    form = SuggestionForm(initial={"user": request.user})
    if request.method=="POST":
        form = SuggestionForm(data=request.POST)
        # below line of code returns true if suggestion_type ==
        # 'feature'. Returns False if == 'bug fix'. Returned as String
        is_feature = request.POST.get("suggestion_type")
        if form.is_valid():
            if is_feature=='True':
                form.save()
    
    return render(request, 'add_suggestion.html', {"form": form})