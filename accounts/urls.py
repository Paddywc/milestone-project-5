from .views import create_user, login_user
from django.conf.urls import url 

urlpatterns = [
    url(r'^signup/$', create_user, name='signup'),
    url(r'^login/$', login_user, name='login')
    ]