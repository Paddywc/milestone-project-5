from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect
from market.models import StoreItem
from django.urls import reverse

from .helpers import set_current_url_as_session_url, return_all_suggestions, return_all_bugs, get_suggestion_object_for_id
from .forms import SuggestionForm
from market.cart import Cart
from market.coins import return_user_coins, get_coins_price, remove_coins, return_all_store_coin_options, return_minimum_coins_purchase

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
            set_current_url_as_session_url(request)
            coins_store_item_id = request.POST.get("purchaseCoinsSelect")
            coins_store_item = get_object_or_404(StoreItem, id=coins_store_item_id)
            cart = Cart(request)
            cart.add(item=coins_store_item)
            return HttpResponseRedirect(reverse('pay'))
        
        else:
            print("this is running")
            form = SuggestionForm(data=request.POST)
            # below line of code returns true if suggestion_type ==
            # 'feature'. Returns False if == 'bug fix'. Returned as String
            is_feature = request.POST.get("suggestion_type")
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
    suggestion = get_suggestion_object_for_id(id)
    return render(request, "view.html", {"suggestion": suggestion})
    
    