import stripe
from django.conf import settings

from .cart import Cart
from .coins import add_coins
from .models import Delivery, Order, OrderItem


def process_stripe_payment(request):
    """
    from stipe documentation
    https://stripe.com/docs/charges
    """
    stripe.api_key = settings.STRIPE_SECRET
    # changed from value in docs: token = request.form['stripeToken'] 
    # fixed bug: 'WSGIRequest' object has no attribute 'form'
    token = request.POST['stripeToken']

    cart = Cart(request)
    payment_amount = cart.get_total_price()
    payment_amount_in_cents = int(payment_amount * 100)
    charge = stripe.Charge.create(
        amount=payment_amount_in_cents,
        currency='eur',
        description='UnicornAttractor purchase',
        source=token,
    )


def process_order(request, user, transaction=0):
    """
    Adds coins to account if they are included
    in order
    """
    try:
        delivery_pk = request.POST.get("deliverySelection")
        delivery_object = Delivery.objects.get(pk=delivery_pk)
        order = Order(user=user, delivery_address=delivery_object)
    except:
        order = Order(user=user)
    order.save()

    cart = Cart(request)
    for item in cart:
        if item["item"].is_coins:
            add_coins(user, (item["item"].coins_amount * item["quantity"]), transaction)
        order_item = OrderItem(order=order, item=item["item"], quantity=item["quantity"],
                               total_purchase_price=item["total_price"])
        order_item.save()

    cart.clear()


def cart_contains_item_needing_delivery(request):
    """
    Returns True if the cart contains at least one 
    item with delivery_required == True. Returns False otherwise
    """

    cart = Cart(request)
    for item in cart:
        if item["item"].delivery_required:
            return True
    return False
