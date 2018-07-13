from .models import Suggestion, Upvote, Comment, SuggestionAdminPage
from django.db.models import Count
from .forms import SuggestionForm

def set_current_url_as_session_url(request):
    """
    """
    request.session["session_url"] = str(request.build_absolute_uri())

def return_current_features(sorting="oldest"):
    """
    Returns all features (not bugs) in the current 
    voting cycle along with their upvote count.
    Ordered by argument value
    """
    if sorting == "oldest":
        sorting ="date_time"
    elif sorting == "newest":
        sorting= "-date_time"
    elif sorting == "comments":
        sorting = "-comments"
    else:
        sorting = "-upvotes"
    
    return Suggestion.objects.filter(is_feature=True, suggestionadminpage__in_current_voting_cycle=True).annotate(upvotes=Count("upvote")).annotate(comments=Count("comment")).order_by(sorting)

def return_all_bugs(sorting="oldest"):
    """
    Returns all bugs in database  along with 
    their upvote count. Ordered in descending 
    order by upvote count
    """
    
    if sorting == "oldest":
        sorting ="date_time"
    elif sorting == "newest":
        sorting= "-date_time"
    elif sorting == "comments":
        sorting = "-comments"
    else:
        sorting = "-upvotes"

    return Suggestion.objects.filter(is_feature=False).annotate(upvotes=Count("upvote")).annotate(comments=Count("comment")).order_by(sorting)
    

def return_public_suggestion_comments(suggestion, comment_sorting="oldest"):
    """
    Excludes admin comments
    """
    if comment_sorting == "oldest":
        comment_sorting ="date_time"
    elif comment_sorting == "newest":
        comment_sorting= "-date_time"
    else:
        comment_sorting = "-upvotes"
    
    
    return Comment.objects.filter(suggestion=suggestion, admin_page_comment=False).annotate(upvotes=Count("upvote")).annotate(comments=Count("comment")).order_by(comment_sorting)
    
    
def return_admin_suggestion_comments(suggestion):
    """
    """
    
    return Comment.objects.filter(suggestion=suggestion, admin_page_comment=True).order_by("date_time").annotate(upvotes=Count("upvote"))
    
def update_suggestion_admin_page(form):
  
    row = SuggestionAdminPage.objects.get(suggestion=form.cleaned_data["suggestion"])
    row.status = form.cleaned_data["status"]
    row.developer_assigned = form.cleaned_data["developer_assigned"]
    row.priority = form.cleaned_data["priority"]
    row.date_started = form.cleaned_data["date_started"]
    row.estimated_days_to_complete = form.cleaned_data["estimated_days_to_complete"]
    row.expected_completion_date = form.cleaned_data["expected_completion_date"]
    row.github_branch = form.cleaned_data["github_branch"]
    row.in_current_voting_cycle = form.cleaned_data["in_current_voting_cycle"]
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