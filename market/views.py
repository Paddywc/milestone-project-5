from django.shortcuts import render, redirect, get_object_or_404
from .models import StoreItem
from .cart import Cart
# Create your views here.
def render_store(request):
    """
    from ecommerce project
    """
    store_items = StoreItem.objects.all()
    return render(request, "store.html", {"store_items": store_items})
    
    


def cart_add(request, item_id):
    """
    code partly from:
    https://muva.co.ke/blog/creating-shopping-cart-views-shop-products-django-2-0-python-3-6/
    """
    cart = Cart(request)
    item = get_object_or_404(StoreItem, id=item_id)
    cart.add(item=item)
    return redirect('store')


def cart_remove(request, item_id):
    """
    code  from
    https://muva.co.ke/blog/creating-shopping-cart-views-shop-products-django-2-0-python-3-6/
    """
    cart = Cart(request)
    item = get_object_or_404(StoreItem, id=item_id)
    cart.remove(item)
    return redirect('store')