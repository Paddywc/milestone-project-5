from django.shortcuts import get_object_or_404
from .cart import Cart
from .models import StoreItem
from .coins import return_minimum_coins_purchase
from django.http import HttpResponseRedirect
from django.urls import reverse
import market.suggestion_promotion_discounts as discounts 

def set_current_url_as_session_url(request):
    """
    """
    request.session["session_url"] = str(request.build_absolute_uri())


def retrieve_session_url(request):
    """
    """
    try:
        return request.session["session_url"]
    except:
        return False
        
        
        
def purchase_coins_for_action(request):
    """
    """
    set_current_url_as_session_url(request)
    coins_store_item_id = request.POST.get("purchaseCoinsSelect")
    coins_store_item = get_object_or_404(StoreItem, id=coins_store_item_id)
    cart = Cart(request)
    cart.add(item=coins_store_item)
    return HttpResponseRedirect(reverse('pay'))
    
def purchase_coins_for_feature_promotion(request, user_coins, prices):
    """
    """
    set_current_url_as_session_url(request)
    price =prices["{}".format(request.POST.get("promotionDays"))]
    coins = return_minimum_coins_purchase(price, user_coins)
    cart = Cart(request)
    cart.add(coins)
    return HttpResponseRedirect(reverse('pay'))
    
def get_promote_feature_discount_rates():
    """
    """
    return {2: discounts.two, 3: discounts.three, 4:discounts.four, 5:discounts.five}
    
    
