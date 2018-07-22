from django.db import models
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
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
        
class TestModels(TestCase):
    
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
        suggestion_3 = Suggestion( is_feature=False, user=user_2, title="Test Suggestion 3", details="Any old detials", delay_submission=False)
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
        
        
        
    def test_suggestion_suggestion_defaults_as_desired(self):
        """
        Test to check that when creating a Suggestion object, default values
        are assigned as follows: is_feature: False, date_time: now, delay_submission:
        False
        """
        
        users = User.objects.all()
        random_user = choice(users)
        
        new_suggestion = Suggestion(title="Testing Defaults",user=random_user)
        new_suggestion.save()
        
        retrieved_suggestion = Suggestion.objects.get(title="Testing Defaults")
        self.assertFalse(retrieved_suggestion.is_feature)
        self.assertFalse(retrieved_suggestion.delay_submission)
        
        today = datetime.date.today()
        suggestion_date = new_suggestion.date_time.date()
        self.assertEqual(today, suggestion_date)
    
    def test_can_not_create_suggestion_without_user(self):
        """
        Test to check that a Suggestion object can not be created 
        without a user
        """
        with self.assertRaises(IntegrityError):
            without_user = Suggestion(title="Without User")
            without_user.save()
        
        

    def test_suggestion_admin_page_defaults_correctly(self):
        """
        Test to check that if unspecified, a SuggestionAdminPage object defaults
        the following values: status:0, priority:1, in_current_voting_cycle:True,
        current_winner:False
        """
        all_suggestions = Suggestion.objects.all()
        random_suggestion = choice(all_suggestions)
        
        new_suggestion_admin_object = SuggestionAdminPage(suggestion=random_suggestion)
        new_suggestion_admin_object.save()
        
        self.assertEqual(new_suggestion_admin_object.status, 0)
        self.assertEqual(new_suggestion_admin_object.priority, 1)
        self.assertEqual(new_suggestion_admin_object.in_current_voting_cycle, True)
        self.assertEqual(new_suggestion_admin_object.current_winner, False)
    
    def test_can_not_create_suggestion_admin_page_without_suggestion_foreign_key(self):
        """
        Test to check that a SuggestionAdminPage object can not be created 
        without a suggestion value
        """
        with self.assertRaises(IntegrityError):
            without_suggestion = SuggestionAdminPage()
            without_suggestion.save()
    
    def test_current_winner_value_is_exclusive(self):
        """
        Test to check that if a SuggestionAdminPage object's
        current_winner value is saved as True, all other 
        SuggestionAdminPage objects have this value set to False
        """
        SuggestionAdminPage.objects.all().update(current_winner=False)
        
        all_suggestion_admin_objects = SuggestionAdminPage.objects.all()
        first_winner = all_suggestion_admin_objects[1]
        first_winner.current_winner= True
        first_winner.save()
        self.assertTrue(first_winner.current_winner)
        
        
        second_winner = SuggestionAdminPage.objects.all()[0]
        second_winner.current_winner = True
        second_winner.save()
        self.assertTrue(second_winner.current_winner)
        self.assertNotEqual(first_winner.id, second_winner.id)
        
        retrieved_first_winner = SuggestionAdminPage.objects.get(id=first_winner.id)
        self.assertFalse(retrieved_first_winner.current_winner)
        
    
    def test_date_complete_automatically_set_when_done(self):
        """
        Test to check that a SuggestionAdminPage object's date_completed is
        set to the current date if its status is set to done(3) and it doesn't
        already have a value for date_completed
        """
        
        suggestion_admin_objects = SuggestionAdminPage.objects.all()
        random_admin_object = choice(suggestion_admin_objects)
        random_admin_object.status = 3
        random_admin_object.save()
        
        retrieved_completed_admin_object = SuggestionAdminPage.objects.get(id = random_admin_object.id)
        current_date = datetime.date.today()
        self.assertEqual(retrieved_completed_admin_object.date_completed, current_date)
        
        SuggestionAdminPage.objects.all().update(date_completed=None, status=1)
        
        new_random_object = choice(SuggestionAdminPage.objects.all())
        not_today = (current_date - datetime.timedelta(days=3))
        new_random_object.date_completed = not_today
        new_random_object.status = 3
        new_random_object.save()
        
        retrieved_second_completed_object = SuggestionAdminPage.objects.get(id=new_random_object.id)
        self.assertNotEqual(retrieved_second_completed_object.date_completed, current_date)
        self.assertEqual(retrieved_second_completed_object.date_completed, not_today)
        
    
    def test_comment_objects_default_correctly(self):
        """
        Test to check that when creating a comment object, admin_page_comment defaults
        to False, and date_time defaults to the current date and time
        """
    
        random_user = choice(User.objects.all())
        random_suggestion = choice(Suggestion.objects.all())
        new_comment = Comment(user=random_user, suggestion=random_suggestion)
        new_comment.save()
        
        self.assertEqual(str(new_comment.admin_page_comment), "False")
        self.assertEqual(new_comment.date_time.date(), datetime.date.today())
        
        
    def test_can_not_create_comment_without_user(self):
        """
        Test to check that an integrity error will be thrown if there
        is an attempt to save a Comment without providing a user
        """
        with self.assertRaises(IntegrityError):
            random_suggestion = choice(Suggestion.objects.all())
            without_user = Comment(suggestion=random_suggestion)
            without_user.save()
            
    def test_can_not_create_comment_without_suggestion(self):
        """
        Test to check that an integrity error will be thrown if there
        is an attempt to save a Comment without providing a suggestion
        """
        with self.assertRaises(IntegrityError):
            random_user = choice(User.objects.all())
            without_suggestion = Comment(user=random_user)
            without_suggestion.save()
            
    def test_can_not_add_upvote_without_user(self):
        """
        Test to check that an integrity error will be thrown if there
        is an attempt to save an Upvote without providing a user
        """
        with self.assertRaises(IntegrityError):
            new_upvote = Upvote()
            new_upvote.save()
            
            
    def test_only_user_required_for_upvote(self):
        """
        Test to check that an Upvote can be created if only 
        a value for user is provided
        """
        random_user= choice(User.objects.all())
        new_upvote = Upvote(user=random_user)
        new_upvote.save()
        # For this to run, no error has been raised
        self.assertTrue(True)
        
        
    
        
        
        