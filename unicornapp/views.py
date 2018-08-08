from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

import market.coin_prices.coin_rewards as coin_rewards
from accounts.forms import UserSignupForm
from accounts.models import User
from market.coins import add_coins
from market.models import Order, UserCoinHistory, OrderItem
from usersuggestions.models import Upvote, SuggestionAdminPage
from usersuggestions.voting import get_voting_end_date


def render_home(request):
    """
    Renders UnicornAttractor home page.
    Post request occurs when user submits signup form
    """
    form = UserSignupForm
    voting_end_date = get_voting_end_date()
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            if settings.COINS_ENABLED:
                add_coins(new_user, coin_rewards.signup, 5)
                login(request, new_user)
                messages.info(request, "Your account has been created. Welcome {}!".format(new_user.username))
    return render(request, "home.html", {"form": form, "voting_end_date": voting_end_date})


def get_userpage_values(user):
    """
    Returns a dictionary with all the values required
    to render a userpage
    """
    votes = Upvote.objects.filter(user=user).order_by("-date_time")
    purchases = Order.objects.filter(user=user).order_by("-date_time")
    coin_history = UserCoinHistory.objects.filter(user=user).order_by("-date_time")
    suggestions = SuggestionAdminPage.objects.filter(suggestion__user=user).order_by("-suggestion__date_time")

    for purchase in purchases:
        purchase.items = OrderItem.objects.filter(order=purchase)
        purchase.total_cost = 0
        for item in purchase.items:
            purchase.total_cost += item.total_purchase_price

    values_dictionary = {"purchases": purchases,
                         "coin_history": coin_history, "votes": votes, "suggestions": suggestions
                         }

    return values_dictionary


@login_required()
def render_userpage(request, user_id):
    """
    Returns the userpage for the argument user. If it is
    not the current user's userpage, redirect to issue_tracker page
    """
    user = get_object_or_404(User, id=user_id)
    if request.user == user:
        values = get_userpage_values(user)
        return render(request, "userpage.html", {"user": user,
                                                 "votes": values["votes"], "purchases": values["purchases"],
                                                 "coin_history": values["coin_history"],
                                                 "suggestions": values["suggestions"],
                                                 })

    else:
        return redirect("issue_tracker")
