from django.contrib import admin
from .models import StoreItem, CoinsPurchase, Order, Delivery, OrderItem, UserCoins, UserCoinHistory


class OrderItemAdminInline(admin.TabularInline):
    model = OrderItem
    
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemAdminInline,)
    
    
admin.site.register(StoreItem)
admin.site.register(CoinsPurchase)
admin.site.register(Order, OrderAdmin)
admin.site.register(Delivery) 
admin.site.register(UserCoins) 
admin.site.register(UserCoinHistory) 
