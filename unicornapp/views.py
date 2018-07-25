from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import UserSignupForm
from django.contrib.auth import login
from market.coins import add_coins
from django.conf import settings
import market.coin_prices.coin_rewards as coin_rewards

# Create your views here.
def render_home(request):
    """
    """
    form = UserSignupForm
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            if settings.COINS_ENABLED:
                add_coins(new_user, coin_rewards.signup, 5)
                login(request, new_user)
    return render(request, "home.html", {"form": form})