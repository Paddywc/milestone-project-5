from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404

from .cart import Cart
from .checkout import process_stripe_payment, process_order, \
    cart_contains_item_needing_delivery
from .forms import DeliveryForm
from .helpers import retrieve_session_url
from .models import StoreItem, CoinsPurchase, Delivery



def render_store(request):
    """
    From ecommerce project. Renders store page
    """
    store_items = StoreItem.objects.all()
    return render(request, "store.html", {"store_items": store_items})

def cart_add(request, item_id):
    """
    Adds item to cart. Code partly from:
    https://muva.co.ke/blog/creating-shopping-cart-views-shop-products-django-2-0-python-3-6/
    """
    cart = Cart(request)
    item = get_object_or_404(StoreItem, id=item_id)
    cart.add(item)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cart_remove(request, item_id):
    """
    Removes item to cart. Code partly from:
    https://muva.co.ke/blog/creating-shopping-cart-views-shop-products-django-2-0-python-3-6/
    """
    cart = Cart(request)
    item = get_object_or_404(StoreItem, id=item_id)
    cart.remove(item)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def view_cart(request):
    """
    Renders cart.html page
    """
    return render(request, "cart.html")


@login_required()
def delivery(request):
    """
    Renders form to create a Delivery object.
    On post, save this form(if it is valid) and
    redirect to pay page
    """
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
    Renders pay page. Post request can only occur if stripe
    accepts payment. Redirect to delivery page if cart has an item
    that needs delivery and user has no delivery addresses in database.
    """
    if request.method == "POST":
        process_stripe_payment(request)
        process_order(request, request.user, 4)
        redirect_url = retrieve_session_url(request)
        messages.success(request, "Purchase successful. Thank you")

        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect("store")

    user_addresses = Delivery.objects.filter(user=request.user)
    cart_contains_delivery_item = cart_contains_item_needing_delivery(request)

    cart = Cart(request)
    if cart_contains_delivery_item and (len(user_addresses) == 0):
        return redirect("delivery")

    elif len(cart) == 0:
        return redirect("store")

    else:
        return render(request, 'pay.html',
                      {"addresses": user_addresses, "cart_contains_delivery_item": cart_contains_delivery_item,
                       "cart": cart,
                       })


@login_required()
def earn_coins(request):
    """
    Renders earn_coins page. Post request indicates
    that the user has entered a referee email
    """
    coin_purchases = CoinsPurchase.objects.all()
    if request.method == "POST":
        email = request.POST.get("refereeEmail")
        referral_link = "{0}{1}".format(request.get_host(), redirect("referred_signup", request.user.id).url)
        reference_sender_email = request.user.email
        subject = "{} thinks that you'll like UnicornAttractor".format(reference_sender_email)
        body = "Click this link to sign up now: {}".format(referral_link)
        email = EmailMessage(subject, body, to=[email])
        email.send()
        messages.info(request, "Email sent")
    return render(request, "earn_coins.html", {"coin_purchases": coin_purchases})
