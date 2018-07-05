# code largly from: https://muva.co.ke/blog/developing-shopping-cart-class-shop-products-django-2-0-python-3-6/
from decimal import Decimal
from django.conf import settings
from .models  import StoreItem
class Cart(object):
    def __init__(self,request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
      
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
        
    def add(self, item):
        item_id = str(item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0, 'price': str(item.price)}
            
        self.cart[item_id]['quantity'] += 1
        self.save()
        


    def remove(self, StoreItem):
        item_id = str(StoreItem.id)
        if item_id in self.cart:
            if self.cart[item_id]['quantity'] >= 2:
                self.cart[item_id]['quantity'] -= 1
            else:
                del self.cart[item_id]
            self.save()
            
    def __iter__(self):
        item_ids = self.cart.keys()
        items = StoreItem.objects.filter(id__in=item_ids)
        for item in items:
            self.cart[str(item.id)]['item'] = item
 
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
 
        
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
 
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
        
    def get_stripe_price(self):
        """
        My code. Required to get the correct price
        for Stripe JavaScript payment
        """
        return (sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values()) * 100)

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True


   