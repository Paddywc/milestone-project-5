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
    if request.method=="POST":
        form = SuggestionForm(data=request.POST)
        # below line of code returns true if suggestion_type ==
        # 'feature'. Returns False if == 'bug fix'. Returned as String
        is_feature = request.POST.get("suggestion_type")
        if form.is_valid():
            if is_feature=='True':
                print("this is running")
            form.save()
    
    return render(request, 'add_suggestion.html', {"form": form})