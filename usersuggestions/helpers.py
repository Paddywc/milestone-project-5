from .models import Suggestion, Upvote, Comment, SuggestionAdminPage
from django.db.models import Count

def set_current_url_as_session_url(request):
    """
    """
    request.session["session_url"] = str(request.build_absolute_uri())

def return_all_features():
    """
    Returns all features (not bugs) in database 
    along with their upvote count. Ordered in descending 
    order by upvote count
    """
    return Suggestion.objects.filter(is_feature=True).annotate(upvotes=Count("upvote")).order_by("-upvotes")

def return_all_bugs():
    """
    Returns all bugs in database  along with 
    their upvote count. Ordered in descending 
    order by upvote count
    """
    return Suggestion.objects.filter(is_feature=False).annotate(upvotes=Count("upvote")).order_by("-upvotes")
    

def return_public_suggestion_comments(suggestion):
    """
    Excludes admin comments
    """
    return Comment.objects.filter(suggestion=suggestion, admin_page_comment=False).order_by("date_time").annotate(upvotes=Count("upvote"))
    
    
def return_admin_suggestion_comments(suggestion):
    """
    """
    return Comment.objects.filter(suggestion=suggestion, admin_page_comment=True).order_by("date_time").annotate(upvotes=Count("upvote"))
    
def update_suggestion_admin_page(form):
    row = SuggestionAdminPage.objects.get(suggestion=form.cleaned_data["suggestion"])
    row.status = form.cleaned_data["status"]
    row.developer_assigned = form.cleaned_data["developer_assigned"]
    row.priority = form.cleaned_data["priority"]
    row.date_time_started = form.cleaned_data["date_time_started"]
    row.expected_completion_date_time = form.cleaned_data["expected_completion_date_time"]
    row.github_branch = form.cleaned_data["github_branch"]
    row.save()