from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .helpers import set_current_url_as_session_url, return_all_features, return_all_bugs, return_suggestion_comments
from .forms import SuggestionForm, CommentForm
from market.cart import Cart
from market.coins import return_user_coins, get_coins_price, remove_coins, return_all_store_coin_options, return_minimum_coins_purchase
from market.helpers import purchase_coins_for_action
from .models import Suggestion, Comment, SuggestionAdminPage
from .voting import add_suggestion_upvote_to_database, add_comment_upvote_to_database


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
            # below line of code returns true if is_feature ==
            # 'feature'. Returns False if == 'bug fix'. Returned as String
            is_feature = request.POST.get("is_feature")
            if form.is_valid():
                if is_feature=='True' and settings.COINS_ENABLED:
                    remove_coins(request.user, get_coins_price("Suggestion"))
                    user_coins = return_user_coins(request.user)
            
                saved_suggestion_object = form.save()
                suggestion_admin_page = SuggestionAdminPage(suggestion= saved_suggestion_object)
                suggestion_admin_page.save()
                
                
                
    if (settings.COINS_ENABLED):
        price = get_coins_price("Suggestion")
        user_coins = return_user_coins(request.user)
        minimum_coins = return_minimum_coins_purchase(price, user_coins)
        coin_options = return_all_store_coin_options()
        
    return render(request, 'add_suggestion.html', {"form": form, "coins_enabled": settings.COINS_ENABLED, "user_coins": user_coins, "price":price, "coin_options": coin_options, "minimum_coins": minimum_coins})
    
    
def render_home(request):
    """
    """
    features = return_all_features()
    bugs = return_all_bugs()
    return render(request, "home.html", {"features": features, "bugs": bugs})


def view_suggestion(request, id):
    """
    """
    coins_enabled =settings.COINS_ENABLED

    suggestion = get_object_or_404(Suggestion, id=id)
    comments = return_suggestion_comments(suggestion)
    form = CommentForm(initial={"user": request.user,"suggestion": suggestion})
    
    if request.method=="POST":
        if 'purchaseCoins' in request.POST:
            return purchase_coins_for_action(request)
            
        elif 'postComment' in request.POST:
            form = CommentForm(data=request.POST)
            if form.is_valid():
                form.save()
            
        
    if coins_enabled and request.user.is_authenticated:
        price = get_coins_price("Upvote")
        user_coins = return_user_coins(request.user)
        minimum_coins = return_minimum_coins_purchase(price, user_coins)
        coin_options = return_all_store_coin_options()
        
    else:
        price = None
        user_coins = None
        minimum_coins = None
        coin_options = None 

    if suggestion.is_feature: 
        return render(request, "view_feature.html", {"form":form, "comments": comments, "feature": suggestion, "coins_enabled": coins_enabled, "price": price, "user_coins": user_coins, "minimum_coins": minimum_coins, "coin_options": coin_options})
        
    else:
        return render(request, "view_bug.html", {"form":form, "comments": comments, "bug": suggestion,"coins_enabled": coins_enabled})
        
    
    
    return True
  
@login_required
def upvote_suggestion(request, id):
    """
    """
    if settings.COINS_ENABLED:
        remove_coins(request.user, get_coins_price("Upvote"))
    suggestion = get_object_or_404(Suggestion, id=id)
    add_suggestion_upvote_to_database(request.user, suggestion)
    return redirect("view_suggestion",id)

@login_required
def upvote_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    add_comment_upvote_to_database(request.user, comment)
    return redirect("view_suggestion",comment.suggestion.id)
