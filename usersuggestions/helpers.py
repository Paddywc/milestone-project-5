from .models import Suggestion

def set_current_url_as_session_url(request):
    """
    """
    request.session["session_url"] = str(request.build_absolute_uri())

def return_all_suggestions():
    """
    """
    return Suggestion.objects.filter(suggestion_type=True)
    
def return_all_bugs():
    """
    """
    return Suggestion.objects.filter(suggestion_type=False)