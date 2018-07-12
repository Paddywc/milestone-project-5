from .models import Upvote, SuggestionAdminPage
from django.shortcuts import get_object_or_404

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
    """
    try:
        current_winner = SuggestionAdminPage.objects.get(is_current_winner="True")
        # print(current_winner.expected_completion_date_time)
        return current_winner
    except:
        return False