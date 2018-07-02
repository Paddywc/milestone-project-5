from .views import create_user
from django.conf.urls import url 

urlpatterns = [
    url(r'^signup/$', create_user, name='signup')
    ]