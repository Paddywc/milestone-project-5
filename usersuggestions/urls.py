from django.conf.urls import url

from .views import add_suggestion, view_suggestion, upvote_suggestion, upvote_comment, render_suggestion_admin_page, \
    flag_item, promote_feature, view_data, render_issue_tracker, render_flags_page, flag_response, delete_comment

urlpatterns = [
    url(r'^$', render_issue_tracker, name='issue_tracker'),
    url(r'^sort/(?P<sorting>[-\w]+)$', render_issue_tracker, name='issue_tracker'),
    url(r'^add/$', add_suggestion, name='add_suggestion'),
    url(r'^view/(?P<id>\d+)/(?P<comment_sorting>[-\w]+)', view_suggestion, name="view_suggestion"),
    url(r'^view/(?P<id>\d+)', view_suggestion, name="view_suggestion"),
    url(r'^upvote_suggestion/(?P<id>\d+)', upvote_suggestion, name="upvote_suggestion"),
    url(r'^upvote_comment/(?P<id>\d+)', upvote_comment, name="upvote_comment"),
    url(r'^admin/(?P<id>\d+)', render_suggestion_admin_page, name="admin_page"),
    url(r'^flag/(?P<item_type>[-\w]+)/(?P<item_id>\d+)/(?P<reason>[-\w]+)', flag_item, name="flag"),
    url(r'^promote$', promote_feature, name="promote_feature"),
    url(r'^view_data$', view_data, name="view_data"),
    url(r'^flags$', render_flags_page, name="flags"),
    url(r'^flag_response/(?P<flag_id>\d+)/(?P<result>[-\w]+)$', flag_response, name="flag_response"),
    url(r'^delete_comment/(?P<comment_id>\d+)/(?P<suggestion_id>\d+)$', delete_comment, name="delete_comment"),
]
