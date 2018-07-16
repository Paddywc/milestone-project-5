from .views import create_user, login_user, logout_user, created_referred_user
from django.conf.urls import url , include
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^ref/(?P<ref_user_id>\d+)/signup/$', created_referred_user, name='referred_signup'),
    url(r'^signup/$', create_user, name='signup'),
    url(r'^login/$', login_user, name='login'),
    url(r'^logout/$', logout_user, name='logout'),
    url('^', include('django.contrib.auth.urls')),
    ]