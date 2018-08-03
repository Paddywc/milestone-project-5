# from http://muva.co.ke/blog/lesson-8-developing-context-processor-current-cart-django-2-0-python-3-6/
from .cart import Cart
from .models import UserCoins
from .coins import return_user_coins

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
        return {"usercoins":coins_amount}
    else:
        return {"usercoins": None}