import datetime

from django.conf import settings
from django.db.models import Count

import market.coin_prices.coin_rewards as coin_rewards
from market.coins import add_coins
from .models import Upvote, SuggestionAdminPage, Suggestion


def add_suggestion_upvote_to_database(user, suggestion):
    """
    Creates an Upvote object with the argument user and suggestion
    as foreign keys
    """
    if settings.COINS_ENABLED == False or suggestion.is_feature == False:
        if len(Upvote.objects.filter(user=user, suggestion=suggestion)) == 0:
            upvote = Upvote(user=user, suggestion=suggestion)
            upvote.save()
            return False
        else:
            return True
    else:
        upvote = Upvote(user=user, suggestion=suggestion)
        upvote.save()
        return False


def add_comment_upvote_to_database(user, comment):
    """
    Creates a new upvote with the argument user and comment
    as foreign keys
    """
    if len(Upvote.objects.filter(user=user, comment=comment)) == 0:
        upvote = Upvote(user=user, comment=comment)
        upvote.save()
        return False
    else:
        return True


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
    If a SuggestionAdminPage object does not have an expected_completion_date
    value, set it as the current date + the object's estimated_days_to_complete.
    If the object does not have an estimated_days_to_complete, sets it as 14
    """
    try:
        winner_admin_object = SuggestionAdminPage.objects.get(current_winner=True)
        if winner_admin_object.expected_completion_date == None:
            if winner_admin_object.estimated_days_to_complete:
                estimated_days = winner_admin_object.estimated_days_to_complete
            else:
                estimated_days = 14
            winner_admin_object.expected_completion_date = datetime.date.today() + datetime.timedelta(
                days=estimated_days)
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
    Sets all suggestion's in_current_voting_cycle values to False.
    Make sure to set current winner before calling this function
    """
    SuggestionAdminPage.objects.filter(in_current_voting_cycle=True).update(in_current_voting_cycle=False)


def set_suggestions_success_result():
    """
    For all SuggestionAdminPages in the current voting cycle, if they are the current winner,
    set their was_successful value to True. Otherwise, set their was_successful value to False
    """
    SuggestionAdminPage.objects.filter(in_current_voting_cycle=True, current_winner=False).update(was_successful=False)
    SuggestionAdminPage.objects.filter(in_current_voting_cycle=True, current_winner=True).update(was_successful=True)


def declare_winner():
    """
    Whichever feature suggestions in the current voting cycle has the most upvotes has
    its current_winner value set to True. Adds coins to suggestion's user's account. Amount
    of coins specified in coin_rewards  file
    """
    try:
        winner = Suggestion.objects.filter(is_feature=True, suggestionadminpage__in_current_voting_cycle=True).annotate(
            upvotes=Count("upvote")).latest('upvote')
        winner_admin_object = SuggestionAdminPage.objects.get(suggestion=winner)
        winner_admin_object.current_winner = True
        winner_admin_object.save()
        if settings.COINS_ENABLED:
            add_coins(winner_admin_object.suggestion.user, coin_rewards.suggestion_successful, 8)
    except:
        return False


def trigger_delayed_suggestions():
    """
    All suggestions with a delay_submission value of True are added to the
    current voting cycle. Their delay_submission value is then set to False
    """
    try:
        SuggestionAdminPage.objects.filter(suggestion__delay_submission=True).update(in_current_voting_cycle=True)
        Suggestion.objects.filter(delay_submission=True).update(delay_submission=False)

    except Exception as e:
        print(e)


def end_voting_cycle_if_current_end_date():
    """
    If today is the current voting end date: declare a
    winner and start the next voting cycle
    """
    voting_end_date = get_voting_end_date()
    try:
        if datetime.date.today() == voting_end_date:
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


def return_completed_suggestions():
    """
    Returns all completed suggestions. The date_time of the returned
    suggestions are set as the date_time of completion. The Suggestion's
    date_time in the database is not changed
    """
    suggestions = Suggestion.objects.filter(suggestionadminpage__status=3)
    for suggestion in suggestions:
        suggestion.date_time = SuggestionAdminPage.objects.get(suggestion=suggestion).date_completed

    return suggestions
