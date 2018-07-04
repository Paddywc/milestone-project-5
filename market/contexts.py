# from http://muva.co.ke/blog/lesson-8-developing-context-processor-current-cart-django-2-0-python-3-6/
from .cart import Cart


def cart(request):
    return {'cart': Cart(request)}