from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from .cart import Cart
from .checkout import get_user_delivery_addresses, process_stripe_payment, process_order, \
    cart_contains_item_needing_delivery
from .forms import DeliveryForm
from .helpers import retrieve_session_url
from .models import StoreItem


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
    # return redirect('store')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cart_remove(request, item_id):
    """
    code  from
    https://muva.co.ke/blog/creating-shopping-cart-views-shop-products-django-2-0-python-3-6/
    """
    cart = Cart(request)
    item = get_object_or_404(StoreItem, id=item_id)
    cart.remove(item)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def view_cart(request):
    return render(request, "cart.html")


@login_required()
def delivery(request):
    cart = Cart(request)
    # user value hidden using widget
    # therefore set as current user here
    form = DeliveryForm(initial={"user": request.user})
    if request.method == "POST":
        form = DeliveryForm(request.POST)
        # form.user_id = request.user
        if form.is_valid():
            form.save()
            return redirect('pay')

    return render(request, 'delivery.html', {"form": form})


@login_required()
def pay(request):
    """
    Post request can only occur if stripe accepts payment. Redirect
    to delivery page if cart has an item that needs delivery and 
    user has no delivery addresses in database.
    """

    if request.method == "POST":
   
        process_stripe_payment(request)
        process_order(request, request.user, 4)
        redirect_url = retrieve_session_url(request)
        if redirect_url:
            return redirect(redirect_url)
        else:
            return (redirect("store"))

    user_addresses = get_user_delivery_addresses(request.user)
    cart_contains_delivery_item = cart_contains_item_needing_delivery(request)
    
    
    cart = Cart(request)
    if cart_contains_delivery_item and (len(user_addresses)==0):
        return redirect("delivery")
    
    elif len(cart)==0:
        return redirect("store")
        
    else:
        return render(request, 'pay.html',
                  {"addresses": user_addresses, "cart_contains_delivery_item": cart_contains_delivery_item})

@login_required()
def earn_coins(request):
    """
    """
    if request.method == "POST":
        email = request.POST.get("refereeEmail")
        referral_link = "{0}{1}".format(request.get_host(), redirect("referred_signup", request.user.id).url)
        reference_sender_email = request.user.email
        subject = "{} thinks that you'll like UnicorAttractor".format(reference_sender_email)
        body = "click this link to sign up now: {}".format(referral_link)
        email = EmailMessage(subject, body, to=[email])
        email.send()
    return render(request, "earn_coins.html")
