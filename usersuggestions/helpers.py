from .models import Suggestion, Upvote, Comment
from django.db.models import Count

def set_current_url_as_session_url(request):
    """
    """
    request.session["session_url"] = str(request.build_absolute_uri())

def return_all_suggestions():
    """
    Returns all suggestions (not bugs) in database 
    along with their upvote count. Ordered in descending 
    order by upvote count
    """
    return Suggestion.objects.filter(is_suggestion=True).annotate(upvotes=Count("upvote")).order_by("-upvotes")

def return_all_bugs():
    """
    Returns all bugs in database  along with 
    their upvote count. Ordered in descending 
    order by upvote count
    """
    return Suggestion.objects.filter(is_suggestion=False).annotate(upvotes=Count("upvote")).order_by("-upvotes")
    

def return_suggestion_comments(suggestion):
    """
    """
    return Comment.objects.filter(suggestion=suggestion).order_by("date_time")