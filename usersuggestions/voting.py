from .models import Upvote, SuggestionAdminPage, Suggestion
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.conf import settings
import datetime
import market.coin_rewards as coin_rewards
from market.coins import add_coins


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
       
       
def set_expected_compilation_date_if_none_exists():
    """
    """
    try:
        winner_admin_object = SuggestionAdminPage.objects.get(current_winner=True)
        if winner_admin_object.expected_completion_date == None:
            if winner_admin_object.estimated_days_to_complete:
                estimated_days = winner_admin_object.estimated_days_to_complete
            else:
                estimated_days = 14
            winner_admin_object.expected_completion_date = datetime.date.today() + datetime.timedelta(days=estimated_days)
            winner_admin_object.save()
    except:
        return False
        
def set_current_voting_cycle_as_true_for_all_suggestions():
    """
    For testing
    """
    SuggestionAdminPage.objects.filter(suggestion__delay_submission=False).update(in_current_voting_cycle=True)
    SuggestionAdminPage.objects.filter(suggestion__delay_submission=True).update(in_current_voting_cycle=False)
        
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
    Note that this also adds coins
    """
    try:        
        winner = Suggestion.objects.filter(is_feature=True, suggestionadminpage__in_current_voting_cycle=True).annotate(upvotes=Count("upvote")).latest('upvote')
        winner_admin_object = SuggestionAdminPage.objects.get(suggestion=winner)
        winner_admin_object.current_winner=True
        winner_admin_object.save()
        if settings.COINS_ENABLED:
            add_coins(winner_admin_object.suggestion.user, coin_rewards.suggestion_successful, 8) 
    except:
        return False
        
        
def trigger_delayed_suggestions():
    """
    """
    try:
        SuggestionAdminPage.objects.filter(suggestion__delay_submission=True).update(in_current_voting_cycle=True)
        Suggestion.objects.filter(delay_submission=True).update(delay_submission=False)
        
        
    except Exception as e:
        print(e)
        
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
           trigger_delayed_suggestions()
           set_expected_compilation_date_if_none_exists()
           
        else:
            return False
    except Exception as e:
        print(e)
        return False
        
def return_previous_winners():
    """
    """
    return Suggestion.objects.filter(suggestionadminpage__was_successful=True)