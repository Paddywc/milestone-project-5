from django.conf.urls import url

from .views import add_suggestion, view_suggestion, upvote_suggestion, upvote_comment, render_suggestion_admin_page, \
    flag_item, promote_feature, view_data

urlpatterns = [
    url(r'^add/$', add_suggestion, name='add_suggestion'),
    url(r'^view/(?P<id>\d+)/(?P<comment_sorting>[-\w]+)', view_suggestion, name="view_suggestion"),
    url(r'^view/(?P<id>\d+)', view_suggestion, name="view_suggestion"),
    url(r'^upvote_suggestion/(?P<id>\d+)', upvote_suggestion, name="upvote_suggestion"),
    url(r'^upvote_comment/(?P<id>\d+)', upvote_comment, name="upvote_comment"),
    url(r'^admin/(?P<id>\d+)', render_suggestion_admin_page, name="admin_page"),
    url(r'^flag/(?P<item_type>[-\w]+)/(?P<item_id>\d+)/(?P<reason>[-\w]+)', flag_item, name="flag"),
    url(r'^promote$', promote_feature, name="promote_feature"),
    url(r'^view_data$', view_data, name="view_data")
]
