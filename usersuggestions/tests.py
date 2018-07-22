from django.db import models
from django.test import TestCase
from django.conf import settings
from .voting import add_suggestion_upvote_to_database, add_comment_upvote_to_database, get_voting_end_date, remove_all_suggestions_from_current_voting_cycle, set_expected_compilation_date_if_none_exists, set_suggestions_success_result,  declare_winner, trigger_delayed_suggestions, end_voting_cycle_if_current_end_date, return_previous_winners
from .models import Upvote, Suggestion, Comment, SuggestionAdminPage
from market.models import UserCoins
from accounts.models import User
from random import choice, randint
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
        
        upvote_suggestion_1_1 = Upvote(user=user_1, suggestion= suggestion_1)
        upvote_suggestion_1_1.save()
        upvote_suggestion_2_1 = Upvote(user=user_1, suggestion= suggestion_2)
        upvote_suggestion_2_1.save()
        upvote_suggestion_2_2 = Upvote(user=user_2, suggestion= suggestion_2)
        upvote_suggestion_2_2.save()
        upvote_suggestion_2_3 = Upvote(user=user_1, suggestion= suggestion_2)
        upvote_suggestion_2_3.save()
        
        
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
        
    def test_function_removes_all_suggestions_from_current_voting_cycle(self):
        """
        Test to check that after calling remove_all_suggestions_from_current_voting_cycle,
        all SuggestionAdminPage objects have in_current_voting_cycle set to False. Must
        first establish that at least one of these objects initially has in_current_voting_cycle 
        set to True
        """
        
        at_lease_one_suggestion_in_current_voting_cycle = False
        all_suggestion_admin_objects = SuggestionAdminPage.objects.all()
        for suggestion in all_suggestion_admin_objects:
            if suggestion.in_current_voting_cycle == True:
                at_lease_one_suggestion_in_current_voting_cycle=True
        self.assertTrue(at_lease_one_suggestion_in_current_voting_cycle)
        
        remove_all_suggestions_from_current_voting_cycle()
        
        at_lease_one_suggestion_in_current_voting_cycle = False
        all_suggestion_admin_objects = SuggestionAdminPage.objects.all()
        for suggestion in all_suggestion_admin_objects:
            if suggestion.in_current_voting_cycle == True:
                at_lease_one_suggestion_in_current_voting_cycle=True
        self.assertFalse(at_lease_one_suggestion_in_current_voting_cycle)
        
    
    def test_that_suggestions_was_successful_value_set_as_true_iff_in_current_cycle_and_current_winner(self):
        """
        Test to check that set_suggestions_success_result sets a suggestion admin object's was_successful 
        value to True if, and only if, the object has a True value for both in_current_voting_cycle and 
        current_winner
        """
        SuggestionAdminPage.objects.all().update(in_current_voting_cycle=False, was_successful=False)
        suggestion_admin_pages = SuggestionAdminPage.objects.all()
        
        in_cycle_but_not_successful = suggestion_admin_pages[0]
        in_cycle_but_not_successful.in_current_voting_cycle= True
        in_cycle_but_not_successful.save()
        
        in_cycle_and_successful = suggestion_admin_pages[1]
        in_cycle_and_successful.in_current_voting_cycle=True
        in_cycle_and_successful.current_winner = True
        in_cycle_and_successful.save()
        
        successful_but_not_in_cycle = suggestion_admin_pages[2]
        successful_but_not_in_cycle.current_winner = True
        in_cycle_and_successful.save()
        
        set_suggestions_success_result()
        
        new_in_cycle_but_not_successful = SuggestionAdminPage.objects.get(id = in_cycle_but_not_successful.id)
        self.assertFalse(new_in_cycle_but_not_successful.was_successful)
        
        new_in_cycle_and_successful = SuggestionAdminPage.objects.get(id = in_cycle_and_successful.id)
        self.assertTrue(new_in_cycle_and_successful.was_successful)
        
        new_successful_but_not_in_cycle = SuggestionAdminPage.objects.get(id = in_cycle_but_not_successful.id)
        self.assertFalse(new_successful_but_not_in_cycle.was_successful)
        
        
    def test_to_check_winner_is_most_upvoted_suggestion_in_current_cycle(self):
        """
        To to check that declare_winner sets one suggestion admin page object's
        current_winner value to True. This suggestion should have the most upvotes
        of all suggestions in the current cycle
        """
        SuggestionAdminPage.objects.all().update(in_current_voting_cycle=True, current_winner=False)
        declare_winner()
        winner = SuggestionAdminPage.objects.get(current_winner=True)
        
        upvotes = Upvote.objects.all()
        all_suggestion_upvotes = []
        for upvote in upvotes:
            if upvote.suggestion:
                all_suggestion_upvotes.append(upvote.suggestion.id)
        
        count_dictionary = {}
        for suggestion_id in set(all_suggestion_upvotes):
            count_of_id = {"{}".format(suggestion_id): 0}
            for upvote in all_suggestion_upvotes:
                if upvote == suggestion_id:
                    count_of_id["{}".format(suggestion_id)] +=1
            
            count_dictionary.update(count_of_id)
        
        id_with_highest_count = max(count_dictionary)
        self.assertEqual(winner.suggestion.id, int(id_with_highest_count))
        
        SuggestionAdminPage.objects.all().update(in_current_voting_cycle=True, current_winner=False)
        winner.in_current_voting_cycle=False
        winner.save()
        declare_winner()
        new_winner = SuggestionAdminPage.objects.get(current_winner=True)
        self.assertNotEqual(winner.id, new_winner.id)
        
    
    def test_coins_given_to_winner_if_coints_enabled(self):
        """
        Test to check that if coins are enabled, declare_winner() gives
        coins to the winning suggestion's user
        """
        if settings.COINS_ENABLED:
            
            a_user_has_coins = False
            all_user_coin_rows = UserCoins.objects.all()
            for row in all_user_coin_rows:
                if row.coins > 0:
                    a_user_has_coins=True
            
            self.assertFalse(a_user_has_coins)
            
            declare_winner()
            winner = SuggestionAdminPage.objects.get(current_winner=True)
            winning_user = winner.suggestion.user
            winning_users_coins = UserCoins.objects.get(user=winning_user).coins
            self.assertTrue(int(winning_users_coins)>0)
    
        else:
            declare_winner()
            all_user_coin_rows = UserCoins.objects.all()
            for row in all_user_coin_rows:
                if row.coins > 0:
                    a_user_has_coins=True
            
            self.assertFalse(a_user_has_coins)
        
            
    
    def test_delayed_suggestions_added_to_voting_cycle(self):
        """
        Test to check that trigger_delayed_suggestions adds 
        all delayed suggestions to voting cycle
        """
        
        Suggestion.objects.all().update(delay_submission=False)
        suggestions = Suggestion.objects.all()
        random_suggestion = choice(suggestions)
        random_suggestion.delay_submission = True
        random_suggestion.save()
        
        SuggestionAdminPage.objects.all().update(in_current_voting_cycle=False)
        trigger_delayed_suggestions()
        
        random_suggestion_admin_object = SuggestionAdminPage.objects.get(suggestion=random_suggestion)
        self.assertTrue(random_suggestion_admin_object.in_current_voting_cycle)
        
        suggestion_admin_objects = SuggestionAdminPage.objects.all()
        for suggestion_admin_object in suggestion_admin_objects:
            if suggestion_admin_object != random_suggestion_admin_object:
                self.assertFalse(suggestion_admin_object.in_current_voting_cycle)
                
    def test_voting_cycle_ends_if_current_date(self):
        """
        Test to check that end_voting_cycle_if_current_end_date declares a new 
        winner if the voting end date is today. Function should return false if end date 
        is not today
        """
        
        SuggestionAdminPage.objects.all().update(current_winner=False)
        suggestion_admin_objects = SuggestionAdminPage.objects.all()
        random_admin_object = choice(suggestion_admin_objects)
        random_admin_object.in_current_voting_cycle = False
        random_admin_object.current_winner = True
        random_admin_object.expected_completion_date = datetime.date.today()
        random_admin_object.save()
        
        end_voting_cycle_if_current_end_date()
        
        new_winner = SuggestionAdminPage.objects.get(current_winner=True)
        self.assertNotEqual(new_winner.id, random_admin_object.id)
        
        new_winner.expected_completion_date = (datetime.date.today() + datetime.timedelta(days=3))
        should_be_false = end_voting_cycle_if_current_end_date()
        self.assertEqual(str(should_be_false), "False")
        
    
    def test_can_return_previous_winners(self):
        """
        Test to check that return_previous_winners returns all Suggestion
        objects that were successful
        """
        random_number_from_0_to_3 = randint(0,3)
        all_suggestion_admin_objects = SuggestionAdminPage.objects.all()
        for i in range(random_number_from_0_to_3):
            admin_page_object = all_suggestion_admin_objects[i]
            admin_page_object.was_successful = True
            admin_page_object.save()
            
        previous_winners = return_previous_winners()
        self.assertEqual(len(previous_winners), random_number_from_0_to_3)
        
            