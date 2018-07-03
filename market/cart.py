from django.conf import settings
# code partly from: https://muva.co.ke/blog/developing-shopping-cart-class-shop-products-django-2-0-python-3-6/
class Cart(object):
    def __init__(self,request):
        self.session = request.session
        try:
            cart = self.seassion.get(settings.CART_SESSION_ID)
        except:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        
        
    def add(self, item):
        item_id = str(item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0, 'price': str(item.price)}
            
        self.cart[item_id]['quantity'] += 1
        self.save()
        
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, StoreItem):
        item_id = str(StoreItem.id)
        if item_id in self.cart:
            if self.cart[item_id]['quantity'] >= 2:
                self.cart[item_id]['quantity'] -= 1
            else:
                del self.cart[item_id]
            self.save()
        
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
 
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
 
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True


    