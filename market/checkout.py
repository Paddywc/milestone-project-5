from .cart import Cart
from .models import Delivery

def get_delivery_addresses(user):
    """
    """
    return Delivery.objects.filter(user=user)
    