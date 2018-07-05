from django.shortcuts import render, redirect, get_object_or_404
from .models import StoreItem
from .cart import Cart
from .checkout import get_user_delivery_addresses,  process_stripe_payment, get_full_delivery_object, process_order
from .forms import DeliveryForm
from django.conf import settings
import stripe

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
    return redirect('view_cart')
 
def view_cart(request):
    return render(request, "cart.html")
    
def delivery(request):
    cart = Cart(request)
    # user value hidden using widget
    # therefore set as current user here
    form = DeliveryForm(initial={"user": request.user})
    if request.method=="POST":
        form = DeliveryForm(request.POST)
        # form.user_id = request.user
        if form.is_valid():
            form.save()
            return redirect('pay')
    
    
    return render(request, 'delivery.html', {"form": form})
    
def pay(request):

   
    user = request.user
    user_addresses = get_user_delivery_addresses(user)
    
    if request.method =="POST":
        
        process_stripe_payment(request)
        process_order(request, user)
        
        return redirect('store')
        
    return render(request, 'pay.html', {"addresses": user_addresses})