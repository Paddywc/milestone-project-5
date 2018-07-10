from .models import Suggestion

def set_current_url_as_session_url(request):
    """
    """
    request.session["session_url"] = str(request.build_absolute_uri())

def return_all_suggestions():
    """
    """
    return Suggestion.objects.filter(is_suggestion=True)
    
def return_all_bugs():
    """
    """
    return Suggestion.objects.filter(is_suggestion=False)
    
def get_suggestion_object_for_id(suggestion_id):
    """
    """
    return Suggestion.objects.get(id=suggestion_id)