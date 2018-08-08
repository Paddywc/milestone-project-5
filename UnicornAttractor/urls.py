from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path

from accounts import urls as urls_accounts
from market import urls as urls_cart
from market.views import render_store, earn_coins
from unicornapp.views import render_home, render_userpage
from usersuggestions import urls as urls_suggestions

urlpatterns = [
    path(r'admin/', admin.site.urls),
    url(r'^$', render_home, name="home"),
    url(r'^accounts/', include(urls_accounts)),
    url(r'^store/', render_store, name='store'),
    url(r'^cart/', include(urls_cart)),
    url(r'^suggestions/', include(urls_suggestions)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^user/(?P<user_id>\d+)$', render_userpage, name='userpage'),
    url(r'^earn_coins$', earn_coins, name='earn_coins'),
]
