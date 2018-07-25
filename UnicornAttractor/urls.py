"""UnicornAttractor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.issue_tracker, name='issue_tracker')
Class-based views
    1. Add an import:  from other_app.views import issue_tracker
    2. Add a URL to urlpatterns:  path('', issue_tracker.as_view(), name='issue_tracker')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path

from accounts import urls as urls_accounts
from market import urls as urls_cart
from market.views import render_store, earn_coins
from usersuggestions import urls as urls_suggestions
from usersuggestions.views import render_userpage
from unicornapp.views import render_home

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
