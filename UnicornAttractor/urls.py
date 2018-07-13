"""UnicornAttractor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url , include
from market.views import render_store 

from accounts import urls as urls_accounts
from market import urls as urls_cart
from usersuggestions import urls as urls_suggestions
from usersuggestions.views import render_home

urlpatterns = [
    path(r'admin/', admin.site.urls),
    url(r'^accounts/', include(urls_accounts)),
    url(r'^store/', render_store, name='store'),
    url(r'^cart/', include(urls_cart)),
    url(r'^suggestions/', include(urls_suggestions)),
    url(r'^sort/(?P<sorting>[-\w]+)$', render_home, name='home'),
    url(r'^$', render_home, name='home'),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    
]
