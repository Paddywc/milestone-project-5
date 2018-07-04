from django.urls import path
from django.conf.urls import url , include
from .views import cart_add, cart_remove, view_cart

urlpatterns = [
    url(r'^add/(?P<item_id>\d+)/$', cart_add, name='cart_add'),
    url(r'^remove/(?P<item_id>\d+)/$', cart_remove, name='cart_remove'),
    url(r'^view/$', view_cart, name='view_cart'),
]