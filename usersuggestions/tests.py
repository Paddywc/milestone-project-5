from django.db import models
from django.test import TestCase
from .voting import add_suggestion_upvote_to_database, add_comment_upvote_to_database, get_voting_end_date, set_expected_compilation_date_if_none_exists
from .models import Upvote, Suggestion, Comment, SuggestionAdminPage
from accounts.models import User
from random import choice
import datetime
# Create your tests here.
class TestVoting(TestCase):
    
    @classmethod
    def setUpTestData(cls):

        user_1 = User(username="Test User")
        user_1.save()
        user_2 = User(username="Another Test User", email="example@email.com")
        user_2.save()
        
        suggestion_1 = Suggestion(is_feature=True, user=user_1, title="Test Suggestion 1", details="Any old detials", delay_submission=False)
        suggestion_1.save()
        suggestion_2 = Suggestion(id=2, is_feature=True, user=user_2, title="Test Suggestion 2", details="Any old detials", delay_submission=True)
        suggestion_2.save()
        suggestion_3 = Suggestion.objects.create( is_feature=False, user=user_2, title="Test Suggestion 3", details="Any old detials", delay_submission=False)
        suggestion_3.save()
        
        comment_1 = Comment(user=user_1, suggestion=suggestion_2, comment="test comment")
        comment_1.save()
        comment_2 = Comment(user=user_2, suggestion=suggestion_2, comment="test comment")
        comment_2.save()
        
        admin_page_1 = SuggestionAdminPage(suggestion=suggestion_2,  current_winner=False)
        admin_page_1.save()
        admin_page_2 = SuggestionAdminPage(suggestion=suggestion_1,  current_winner=False)
        admin_page_2.save()
        admin_page_3 = SuggestionAdminPage(suggestion=suggestion_3,  current_winner=False)
        admin_page_3.save()
        
        
        
    def test_can_increase_upvote_size(self):
        """
        Test to check that  add_suggestion/comment_upvote_to_database
        increases the length of the upvote table by 1
        """
        original_update_table = Upvote.objects.all()
        original_update_table_length = len(original_update_table)
        
        users = User.objects.all()
        user = choice(users)
        suggestions = Suggestion.objects.all()
        suggestion = choice(suggestions)
        add_suggestion_upvote_to_database(user, suggestion)
        
        upvote_table_after_suggestion_upvote = Upvote.objects.all()
        upvote_table_after_suggestion_upvote_length = len(upvote_table_after_suggestion_upvote)
        
        self.assertEqual((original_update_table_length+1), upvote_table_after_suggestion_upvote_length)

        comments = Comment.objects.all()
        comment = choice(comments)
        add_comment_upvote_to_database(user, comment)
        
        upvote_table_after_comment_upvote = Upvote.objects.all()
        upvote_table_after_comment_upvote_length = len(upvote_table_after_comment_upvote)
        
        
        self.assertEqual((upvote_table_after_suggestion_upvote_length+1), upvote_table_after_comment_upvote_length)

    def test_voting_end_date_is_expected_completion_date_of_current_winner_or_5_days_away(self):
        """
        Test to check that get_voting_end_date returns the end date of the current 
        winner. If there is no current winner it should return 5 days ahead of the current date
        """
        
        SuggestionAdminPage.objects.all().update(current_winner=False)
        current_date = datetime.date.today()
        end_date_if_no_curent_winner = get_voting_end_date()
        print(end_date_if_no_curent_winner)
        five_days_before_end_date = end_date_if_no_curent_winner - datetime.timedelta(days=5)
        self.assertEqual(current_date, five_days_before_end_date)
        
        suggestion_admin_pages = SuggestionAdminPage.objects.all()
        random_row = choice(suggestion_admin_pages)
        random_row.current_winner = True
        random_row.expected_completion_date = datetime.date(1992,6,3)
        random_row.save()
    
        end_date = get_voting_end_date()
        self.assertEqual(datetime.date(1992,6,3), end_date)
        
        
    def test_expected_completion_date_is_current_date_plus_winners_estimated_completion_date(self):
        """
        Test to check that set_expected_compilation_date_if_none_exists returns the current 
        date + the current winner's estimated_days_to_complete. Should return False if no 
        current winner or current winner already has a completion date. If the current winner
        has no value for estimated_days_to_complete, should return 14 days from the current date 
        """
        
        SuggestionAdminPage.objects.all().update(current_winner=False)
        should_be_false = set_expected_compilation_date_if_none_exists()
        self.assertFalse(should_be_false)
        
        all_rows = SuggestionAdminPage.objects.all()
        random_row = choice(all_rows)
        random_row.current_winner=True
        random_row.expected_completion_date = datetime.date(2010,4,5)
        random_row.save()
        also_should_be_false = set_expected_compilation_date_if_none_exists()
        self.assertFalse(also_should_be_false)
        
        random_row.expected_completion_date = None
        random_row.estimated_days_to_complete = 3
        random_row.save()
        set_expected_compilation_date_if_none_exists()
        current_winner = SuggestionAdminPage.objects.get(current_winner=True)
        three_days_from_now = (datetime.date.today() + datetime.timedelta(days=3))
        self.assertEqual(current_winner.expected_completion_date, three_days_from_now)
        
        current_winner.expected_completion_date = None
        current_winner.estimated_days_to_complete = None
        current_winner.save()
        set_expected_compilation_date_if_none_exists()
        current_winner = SuggestionAdminPage.objects.get(current_winner=True)
        two_weeks_from_now = (datetime.date.today() + datetime.timedelta(days=14))
        self.assertEqual(current_winner.expected_completion_date, two_weeks_from_now)
        
        