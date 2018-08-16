from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404

import market.coin_prices.coin_rewards as coin_rewards
from market.cart import Cart
from market.coins import add_coins
from .forms import UserSignupForm, UserLoginForm
from .models import User


def create_user(request):
    """
    Creates a new (non-admin) user and stores
    them in the database
    """
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            if settings.COINS_ENABLED:
                add_coins(new_user, coin_rewards.signup, 5)
            messages.info(request, "Your account has been created. Please login")
            return redirect("login")
    else:
        form = UserSignupForm()

    return render(request, 'signup.html', {"form": form})


def create_referred_user(request, ref_user_id):
    """
    Creates a new non-admin user. Adds extra coins 
    to both the new user and referee user's UserCoin. 
    Amount of extra coins specified in coin_rewards
    """
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            ref_user = get_object_or_404(User, id=ref_user_id)
            if settings.COINS_ENABLED:
                add_coins(new_user, coin_rewards.signup, 5)
                add_coins(ref_user, coin_rewards.referral, 3)
                add_coins(new_user, coin_rewards.received_referral, 6)
            messages.info(request, "Your account has been created. Please login")
            return redirect("login")
    else:
        form = UserSignupForm()

    return render(request, 'signup.html', {"form": form})


def login_user(request):
    """
    Code from
    https://www.youtube.com/watch?v=XMgF3JwKzgs&list=PL4cUxeGkcC9ib4HsrXEYpQnTOTZE1x0uc&index=22
    Above video showed form.get_user and login
    """
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            messages.success(request, "You have successfuly logged in")
            user = form.get_user()
            login(request, user)
            cart = Cart(request)
            if len(cart) > 0:
                return redirect("view_cart")
            else:
                return redirect("home")
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {"form": form})


def logout_user(request):
    """
    Logs out user
    """
    logout(request)
    messages.success(request, 'You have successfuly logged out')
    return redirect("home")
