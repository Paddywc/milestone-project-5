from django.shortcuts import render
from .models import StoreItem
# Create your views here.
def render_store(request):
    """
    from ecommerce project
    """
    store_items = StoreItem.objects.all()
    return render(request, "store.html", {"store_items": store_items})