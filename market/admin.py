from django.contrib import admin
from .models import StoreItem, Order, Delivery, OrderItem


class OrderItemAdminInline(admin.TabularInline):
    model = OrderItem
    
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemAdminInline,)
    
    
admin.site.register(StoreItem) 
admin.site.register(Order, OrderAdmin)
admin.site.register(Delivery) 
