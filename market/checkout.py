from .cart import Cart
from .models import Delivery
import stripe
from django.conf import settings

def get_user_delivery_addresses(user):
    """
    """
    return Delivery.objects.filter(user=user)
    
def get_full_delivery_object(pk):
    """
    """
    return Delivery.objects.get(pk=pk)
    
def process_stripe_payment(request):
    """
    from stipe documentation
    https://stripe.com/docs/charges
    """
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
    
    