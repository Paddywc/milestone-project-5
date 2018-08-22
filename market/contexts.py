from .cart import Cart
from .coins import return_user_coins
from django.conf import settings


def cart(request):
    return {'cart': Cart(request)}


def usercoins(request):
    """
    Else statement required to avoid error
    when user is not signed in
    """
    if request.user.is_authenticated:
        user = request.user
        coins_amount = return_user_coins(user)
        return {"usercoins": coins_amount}
    else:
        return {"usercoins": None}


def coins_are_enabled(request):
    """
    Used to display or hide values in the 
    base template depending on if coins are 
    enabled in the settings
    """
    return {"coins_are_enabled": settings.COINS_ENABLED}
