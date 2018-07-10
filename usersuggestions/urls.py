from django.conf.urls import url
from .views import add_suggestion, view_suggestion

urlpatterns = [
    url(r'^add/$', add_suggestion, name='add_suggestion'),
    url(r'^view/(?P<id>\d+)', view_suggestion, name="view_suggestion"),
    ]