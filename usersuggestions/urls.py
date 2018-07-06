from django.conf.urls import url
from .views import add_suggestion

urlpatterns = [
    url(r'^add/$', add_suggestion, name='add_suggestion'),
    
    ]