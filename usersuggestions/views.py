from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .helpers import set_current_url_as_session_url, return_all_suggestions, return_all_bugs
from .forms import SuggestionForm
from market.cart import Cart
from market.coins import return_user_coins, get_coins_price, remove_coins, return_all_store_coin_options, return_minimum_coins_purchase
from market.helpers import purchase_coins_for_action
from .models import Suggestion
from .voting import add_upvote_to_database


@login_required()
def add_suggestion(request):
    """
    """
    
    # user value hidden using widget
    # therefore set as current user here
    form = SuggestionForm(initial={"user": request.user})
        
    if request.method=="POST":
        
        # if the user has insufficient coins for suggestion 
        # and opts to purchase more
        if 'purchaseCoins' in request.POST:
            return purchase_coins_for_action(request)
        
        else:
            form = SuggestionForm(data=request.POST)
            # below line of code returns true if is_suggestion ==
            # 'feature'. Returns False if == 'bug fix'. Returned as String
            is_feature = request.POST.get("is_suggestion")
            if form.is_valid():
                if is_feature=='True' and settings.COINS_ENABLED:
                    remove_coins(request.user, get_coins_price("Suggestion"))
                    user_coins = return_user_coins(request.user)
                    
                form.save()
                
                
    if (settings.COINS_ENABLED):
        price = get_coins_price("Suggestion")
        user_coins = return_user_coins(request.user)
        minimum_coins = return_minimum_coins_purchase(price, user_coins)
        coin_options = return_all_store_coin_options()
        
    return render(request, 'add_suggestion.html', {"form": form, "coins_enabled": settings.COINS_ENABLED, "user_coins": user_coins, "price":price, "coin_options": coin_options, "minimum_coins": minimum_coins})
    
    
def render_home(request):
    """
    """
    suggestions = return_all_suggestions()
    bugs = return_all_bugs()
    return render(request, "home.html", {"suggestions": suggestions, "bugs": bugs})


def view_suggestion(request, id):
    """
    """
    suggestion = get_object_or_404(Suggestion, id=id)
    
    coins_enabled =settings.COINS_ENABLED
    
    if request.method=="POST":
        if 'purchaseCoins' in request.POST:
            return purchase_coins_for_action(request)
        
    if coins_enabled:
        price = get_coins_price("Upvote")
        user_coins = return_user_coins(request.user)
        minimum_coins = return_minimum_coins_purchase(price, user_coins)
        coin_options = return_all_store_coin_options()

    if suggestion.is_suggestion: 
        return render(request, "view_suggestion.html", {"suggestion": suggestion, "coins_enabled": coins_enabled, "price": price, "user_coins": user_coins, "minimum_coins": minimum_coins, "coin_options": coin_options})
        
    else:
        return render(request, "view_bug.html", {"bug": suggestion,"coins_enabled": coins_enabled})
        
    
    
    return True
  
def upvote(request, id):
    """
    """
    if settings.COINS_ENABLED:
        remove_coins(request.user, get_coins_price("Upvote"))
    suggestion = get_object_or_404(Suggestion, id=id)
    add_upvote_to_database(request.user, suggestion)
    return view_suggestion(request, id)
