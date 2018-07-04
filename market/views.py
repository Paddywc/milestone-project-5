from django.shortcuts import render, redirect, get_object_or_404
from .models import StoreItem
from .cart import Cart
from .forms import DeliveryForm, PaymentForm
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
    print(item.name)
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

    form = DeliveryForm()
    if request.method=="POST":
        form = DeliveryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pay')
    
    
    return render(request, 'delivery.html', {"form": form})
    
def pay(request):
    """
    from stipe documentation
    https://stripe.com/docs/charges
    """
   
   
    if request.method =="POST":
        stripe.api_key = settings.STRIPE_SECRET
        
    
        # changed from value in docs: token = request.form['stripeToken'] 
        # fixed bug: 'WSGIRequest' object has no attribute 'form'
        token = request.POST['stripeToken'] 
        
        charge = stripe.Charge.create(
            amount=999,
            currency='usd',
            description='Example charge',
            source=token,
        )
        return redirect('store')
        
    return render(request, 'pay.html')