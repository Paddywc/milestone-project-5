from .models import Upvote, SuggestionAdminPage, Suggestion
from django.shortcuts import get_object_or_404
from django.db.models import Count
import datetime

def add_suggestion_upvote_to_database(user, suggestion):
    """
    """
    upvote = Upvote(user=user, suggestion=suggestion)
    upvote.save()
    
def add_comment_upvote_to_database(user, comment):
    upvote = Upvote(user=user, comment=comment)
    upvote.save()
    
def get_voting_end_date():
    """
    Returns the expected completion date of the current
    winner. If there is no current winner, returns the date
    3 days from the current date
    """
    try:
        current_winner = SuggestionAdminPage.objects.get(current_winner="True")
        return current_winner.expected_completion_date 
    except:
        return datetime.date.today() + datetime.timedelta(days=5)
       
       
def set_expected_compilation_date_if_none_exists(suggestion_admin_page_object):
    """
    """
    try:
        if suggestion_admin_page_object.expected_completion_date == None:
            estimated_days = suggestion_admin_page_object.estimated_days_to_complete
            suggestion_admin_page_object.expected_completion_date = datetime.date.today() + datetime.timedelta(days=estimated_days)
            suggestion_admin_page_object.save()
    except:
        return False
        
def set_current_voting_cycle_as_true_for_all_suggestions():
    """
    For testing
    """
    SuggestionAdminPage.objects.all().update(in_current_voting_cycle=True)
        
def remove_all_suggestions_from_current_voting_cycle():
    """
    Make sure to set current winner before calling this function
    """
    SuggestionAdminPage.objects.filter(in_current_voting_cycle=True).update(in_current_voting_cycle=False)
    
def set_suggestions_success_result():
    """
    """
    SuggestionAdminPage.objects.filter(in_current_voting_cycle=True, current_winner=False).update(was_successful=False)
    SuggestionAdminPage.objects.filter(in_current_voting_cycle=True, current_winner=True).update(was_successful=True)
        
def declare_winner():
    """
    """
    try:        
        winner = Suggestion.objects.filter(is_feature=True, suggestionadminpage__in_current_voting_cycle=True).annotate(upvotes=Count("upvote")).latest('upvote')
        winner_admin_object = SuggestionAdminPage.objects.get(suggestion=winner)
        winner_admin_object.current_winner=True
        winner_admin_object.save()
    except:
        return False
 
        
def end_voting_cycle_if_current_end_date():
    """
    """
    voting_end_date = get_voting_end_date()
    # if datetime.date.today() == voting_end_date:
    # for testing:
    try:
        if datetime.date.today() != voting_end_date:
           declare_winner()
           set_suggestions_success_result()
           remove_all_suggestions_from_current_voting_cycle()
           set_expected_compilation_date_if_none_exists(winner_admin_object)
           
        else:
            return False
    except Exception as e:
        print(e)
        return False