from django.conf.urls import url
from .views import add_suggestion, view_suggestion, upvote_suggestion, upvote_comment

urlpatterns = [
    url(r'^add/$', add_suggestion, name='add_suggestion'),
    url(r'^view/(?P<id>\d+)', view_suggestion, name="view_suggestion"),
    url(r'^upvote_suggestion(?P<id>\d+)', upvote_suggestion, name="upvote_suggestion"),
    url(r'^upvote_comment(?P<id>\d+)', upvote_comment, name="upvote_comment"),
    ]