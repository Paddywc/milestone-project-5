from django.conf.urls import url, include

from .views import create_user, login_user, logout_user, create_referred_user

urlpatterns = [
    url(r'^ref/(?P<ref_user_id>\d+)/signup/$', create_referred_user, name='referred_signup'),
    url(r'^signup/$', create_user, name='signup'),
    url(r'^login/$', login_user, name='login'),
    url(r'^logout/$', logout_user, name='logout'),
    url('^', include('django.contrib.auth.urls')),
]
