from django.shortcuts import render
from .forms import SuggestionForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from market.coins import return_user_coins, get_coins_price, remove_coins

@login_required()
def add_suggestion(request):
    """
    """
    if (settings.COINS_ENABLED):
        user_coins = return_user_coins(request.user)
        price = get_coins_price("Suggestion")
    else:
        user_coins = False
        price = False
    # user value hidden using widget
    # therefore set as current user here
    form = SuggestionForm(initial={"user": request.user})
    if request.method=="POST":
        form = SuggestionForm(data=request.POST)
        # below line of code returns true if suggestion_type ==
        # 'feature'. Returns False if == 'bug fix'. Returned as String
        is_feature = request.POST.get("suggestion_type")
        if form.is_valid():
            if is_feature=='True' and settings.COINS_ENABLED:
                remove_coins(request.user, price)
                user_coins = return_user_coins(request.user)
                
        form.save()
    return render(request, 'add_suggestion.html', {"form": form, "coins_enabled": settings.COINS_ENABLED, "user_coins": user_coins, "price":price})