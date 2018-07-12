from .models import Suggestion, Upvote, Comment, SuggestionAdminPage
from django.db.models import Count
from .forms import SuggestionForm

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
    row.date_time_started = form.cleaned_data["date_started"]
    row.estimated_completion_time = form.cleaned_data["estimated_completion_time"]
    row.expected_completion_date_time = form.cleaned_data["expected_completion_date"]
    row.github_branch = form.cleaned_data["github_branch"]
    row.is_current_winner = form.cleaned_data["is_current_winner"]
    row.save()
    
def set_initial_session_form_title_as_false(request):
    """
    If there is no set form_title value in 
    the session, set it as False
    """
    try:
        x = request.session["form_title"]
    except:
        request.session["form_title"] = False
        
        
def return_previous_suggestion_form_values_or_empty_form(request):
    """
    If there are previous suggestion form values saved in the session,
    return a form prepopulated with these values. Otherwise return 
    an empty form.
    """
    if request.session["form_title"] != False:
        return SuggestionForm(initial={"user": request.user, "is_feature": True, "details": request.session["form_details"], "title": request.session["form_title"]})
        
    else:
        # user value hidden using widget
        # therefore set as current user here
        return SuggestionForm(initial={"user": request.user})
        
def set_session_form_values_as_false(request):
    """
    For use in add_suggestion function
    """
    request.session["form_title"] = False
    request.session["form_details"] = False