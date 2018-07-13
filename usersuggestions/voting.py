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
        current_winner = SuggestionAdminPage.objects.get(is_current_winner="True")
        return current_winner.expected_completion_date 
    except:
        return datetime.date.today() + datetime.timedelta(days=5)
        
        
def declare_winner_if_voting_end_date():
    """
    """
    voting_end_date = get_voting_end_date()
    # if datetime.date.today() == voting_end_date:
    # for testing:
    if datetime.date.today() == voting_end_date:
        winner = Suggestion.objects.filter(is_feature=True).annotate(upvotes=Count("upvote")).latest('upvote')
        winner_admin_object = SuggestionAdminPage.objects.get(suggestion=winner)
        winner_admin_object.is_current_winner=True
        winner_admin_object.save()
        
    else:
        return False
        
    