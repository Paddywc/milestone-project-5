from django.shortcuts import get_object_or_404
from .cart import Cart
from .models import StoreItem
from django.http import HttpResponseRedirect
from django.urls import reverse


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