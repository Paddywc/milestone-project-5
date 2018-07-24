from django.db import models
from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.shortcuts  import get_object_or_404
from urllib.parse import urlencode
from .voting import add_suggestion_upvote_to_database, add_comment_upvote_to_database, get_voting_end_date, remove_all_suggestions_from_current_voting_cycle, set_expected_compilation_date_if_none_exists, set_suggestions_success_result,  declare_winner, trigger_delayed_suggestions, end_voting_cycle_if_current_end_date, return_previous_winners
from .models import Upvote, Suggestion, Comment, SuggestionAdminPage, Flag, PromotedFeatureSuggestion
from market.models import UserCoins, CoinsPurchase, StoreItem, UserCoinHistory, Order, OrderItem
from accounts.models import User
from .forms import SuggestionForm, CommentForm, SuggestionAdminPageForm
from .helpers import set_current_url_as_session_url, return_current_features, return_all_current_bugs, return_public_suggestion_comments, return_admin_suggestion_comments, set_session_form_values_as_false, set_session_form_values_as_false, return_previous_suggestion_form_values_or_empty_form, get_userpage_values, get_feature_promotion_prices, get_promoted_features, set_initial_session_form_title_as_false
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
        
        new_user = User(username="increase upvote test user", email="iutu@email.com", password="password")
        new_user.save()
        suggestions = Suggestion.objects.all()
        suggestion = choice(suggestions)
        add_suggestion_upvote_to_database(new_user, suggestion)
        
        upvote_table_after_suggestion_upvote = Upvote.objects.all()
        upvote_table_after_suggestion_upvote_length = len(upvote_table_after_suggestion_upvote)
        
        self.assertEqual((original_update_table_length+1), upvote_table_after_suggestion_upvote_length)

        comments = Comment.objects.all()
        comment = choice(comments)
        add_comment_upvote_to_database(new_user, comment)
        
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
        a_user_has_coins = False
        if settings.COINS_ENABLED:
            
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
        
    def test_free_upvotes_limited(self):
        """
        Test to check that a user can't upvote the same comment or 
        bug more than once. If coins are disabled, the same is true
        for suggestion upvotes
        """
        new_user = User(username="limit vote user", email="limit@email.com", password="password")
        new_user.save()
        
        self.assertTrue(len(Upvote.objects.filter(user=new_user))==0)
        
        random_comment = choice(Comment.objects.all())
        add_comment_upvote_to_database(new_user, random_comment)
        self.assertTrue(len(Upvote.objects.filter(user=new_user, comment=random_comment))==1)
        add_comment_upvote_to_database(new_user, random_comment)
        self.assertTrue(len(Upvote.objects.filter(user=new_user, comment=random_comment))==1)
        
        random_bug = choice(Suggestion.objects.filter(is_feature=False))
        add_suggestion_upvote_to_database(new_user, random_bug)
        self.assertTrue(len(Upvote.objects.filter(user=new_user, suggestion=random_bug))==1)
        add_suggestion_upvote_to_database(new_user, random_bug)
        self.assertTrue(len(Upvote.objects.filter(user=new_user, suggestion=random_bug))==1)
        
        if settings.COINS_ENABLED==False:
            random_feature = choice(Suggestion.objects.filter(is_feature=True))
            add_suggestion_upvote_to_database(new_user, random_feature)
            self.assertTrue(len(Upvote.objects.filter(user=new_user, suggestion=random_feature))==1)
            add_suggestion_upvote_to_database(new_user, random_feature)
            self.assertTrue(len(Upvote.objects.filter(user=new_user, suggestion=random_feature))==1)
        
        
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
        
        
    def test_flag_defaults_correctly(self):
        """
        Test to check that when creating a Flag object, unspecified values default 
        as expected. These are: status : 0, date_time: Now
        """
        random_user= choice(User.objects.all())
        random_comment= choice(Comment.objects.all())
        
        new_flag = Flag(flagged_item_type=1, flagged_by=random_user, 
                        comment=random_comment, reason=2)
        new_flag.save()
        
        current_date = datetime.date.today()
        self.assertEqual(new_flag.date_time_marked.date(), current_date)
        self.assertEqual(new_flag.status, 0)
        
    def test_creating_flag_requires_item_type_and_user_and_reason(self):
        """
        Test to check that an integrity error is thrown if an attempt
        is made to save a Flag object without a value for flagged_by, 
        flagged_item_type and reason
        """
        
        with self.assertRaises(IntegrityError):
           
            with transaction.atomic():
                random_user= choice(User.objects.all())
                random_suggestion= choice(Suggestion.objects.all())
                without_item_type = Flag(flagged_by=random_user, 
                        suggestion=random_suggestion, reason=2)
                without_item_type.save()
                
            with transaction.atomic():
                random_suggestion= choice(Suggestion.objects.all())
                without_user = Flag(flagged_item_type=2,
                        suggestion=random_suggestion, reason=2)
                without_user.save()
            
            with transaction.atomic():
                random_user= choice(User.objects.all())
                random_comment= choice(Comment.objects.all())
                without_reason = Flag(flagged_item_type=1, flagged_by=random_user, 
                                    comment=random_comment)
                without_reason.save()
    
    def test_flag_choices_appear_as_expected(self):
        """
        Test to check that the human readable values for a Flag's
        choices appear as expected
        """
        random_user= choice(User.objects.all())
        random_suggestion = choice(Suggestion.objects.all())
        new_flag = Flag(flagged_item_type=2, flagged_by=random_user, suggestion=random_suggestion,
                        reason=0, status=3)
        new_flag.save()
        
        self.assertEqual(new_flag.get_flagged_item_type_display(), "suggestion")
        self.assertEqual(new_flag.get_reason_display(), "Spam")
        self.assertEqual(new_flag.get_status_display(), "done")
        
    def test_user_and_suggestion_and_start_date_and_end_date_required_to_create_user_promoted_feature_suggestion(self):
        """
        Test to check that a user, suggestion, start_date, and end_date are required
        in order to save a PromotedFeatureSuggestion
        """
        with self.assertRaises(IntegrityError):
           
           
            random_user = choice(User.objects.all())
            random_suggestion = choice(Suggestion.objects.all())
            random_start_date = (datetime.date.today() - datetime.timedelta(days=choice(range(30))))
            random_end_date = (datetime.date.today() + datetime.timedelta(days=choice(range(30))))
            
            with transaction.atomic():
                without_user = PromotedFeatureSuggestion(suggestion=random_suggestion, start_date=random_start_date, end_date=random_end_date)
                without_user.save()
                
            with transaction.atomic():
                without_suggestion = PromotedFeatureSuggestion(user=random_user, start_date=random_start_date, end_date=random_end_date)
                without_suggestion.save()
                
            with transaction.atomic():
                without_start_date = PromotedFeatureSuggestion(user=random_user, suggestion= random_suggestion, end_date=random_end_date)
                without_start_date.save()
                
            with transaction.atomic():
                without_end_date = PromotedFeatureSuggestion(user= random_user, suggestion=random_suggestion, start_date=random_start_date)
                without_end_date.save()
            
            
class TestViews(TestCase):
    
    @classmethod
    def setUpTestData(cls):

        user_1 = User(username="Test User")
        user_1.save()
        user_2 = User(username="Another Test User", email="example@email.com")
        user_2.save()
        user_3 = User(username="withpassword", password="password", email="withpassword@email.com")
        user_3.save()
        
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
        
        coins_purchase_1 = CoinsPurchase(name="coins purchase 1", coins_price=200)
        coins_purchase_1.save()
        coins_purchase_2 = CoinsPurchase(name="coins purchase 2", coins_price=500)
        coins_purchase_2.save()
        suggestion_coins_purchase = CoinsPurchase(name="Suggestion", coins_price=500)
        suggestion_coins_purchase.save()
        upvote_coins_purchase = CoinsPurchase(name="Upvote", coins_price=100)
        upvote_coins_purchase.save()
        promote_feature_purchase = CoinsPurchase(name="Feature Suggestion Promotion", coins_price=600)
        promote_feature_purchase.save()
        
        coins_store_item_500= StoreItem(name="500 coins", price=0, delivery_required=False, is_coins=True, coins_amount=500)
        coins_store_item_500.save()
        
        
    def test_get_add_suggestion_page(self):
        """
        Test to check that the add_suggestion page returns a response
        code of 200 and uses the add_suggestion.html template
        """
        # below line of code from: https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        if settings.COINS_ENABLED:
            page = self.client.get(reverse("add_suggestion"), follow=True)
            self.assertEqual(page.status_code, 200)
            self.assertTemplateUsed(page, "add_suggestion.html")
        
    def test_suggestion_added_when_form_posted(self):
        """
        Test to check that a new Suggestion object is successfully created
        on completion of the form
        """
        
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        
        logged_in_user_id = User.objects.get(username="testuser").id
        
        form_data = {"is_feature": True, "title": "post suggestion", "details": "some details", "user": logged_in_user_id}
        response = self.client.post(reverse("add_suggestion"), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        retrieved_suggestion = Suggestion.objects.get(title="post suggestion")
        self.assertEqual(retrieved_suggestion.details, "some details")
        self.assertEqual(retrieved_suggestion.user.username, "testuser")
        self.assertTemplateUsed("view_bug.html")

    def test_redirected_to_pay_page_when_purchasing_coins_to_post_suggestion(self):
        """
        Test to check that if a user clicks purchaseCoins button on add_suggestion 
        page, they are redirected to the pay page
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        response = self.client.post(reverse("add_suggestion"), {"purchaseCoins": "purchaseCoins", "purchaseCoinsSelect": 1}, follow=True)
        self.assertTemplateUsed(response, "pay.html")
        
    def test_form_values_saved_in_session_on_redirect_from_add_suggestion_page(self):
        """
        Test to check that the SuggestionForm values are saved in the session 
        if redirected from add_suggestion page to pay page
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        self.client.post(reverse("add_suggestion"), {"purchaseCoins": "purchaseCoins", "purchaseCoinsSelect": 1, "title": "test title", "details": "test details"}, follow=True)
        session = self.client.session
        self.assertEqual(session["session_url"], "http://testserver/suggestions/add/")
        self.assertEqual(session["form_title"], "test title")
        self.assertEqual(session["form_details"], "test details")
        
        
    def test_get_home_page(self):
        """
        Test to check that the home page returns a response
        code of 200 and uses the home.html template
        """
        page = self.client.get(reverse("home"))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "home.html")
        
    def test_get_view_suggestion_page(self):
        """
        Test to check that the view_suggestion page returns a response
        code of 200 and uses the view_feature.html or view_bug.html template
        """
        page = self.client.get(reverse("view_suggestion", kwargs={"id": 1}))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "view_feature.html")
        
        page = self.client.get(reverse("view_suggestion", kwargs={"id": 3}))
        self.assertTemplateUsed(page, "view_bug.html")
        
        
        
    def test_user_can_comment_on_suggestion(self):
        """
        Test to check that a user can post a comment to 
        a suggestion page
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        logged_in_user_id = User.objects.get(username="testuser").id
        comment_values = {"postComment": "postComment", "user": logged_in_user_id, "suggestion": 1, "comment": "newly added test comment"}
        self.client.post(reverse("view_suggestion", kwargs={"id": 1}),comment_values, follow=True)
        
        retrieved_comment = Comment.objects.get(user__id=logged_in_user_id)
        self.assertEqual(retrieved_comment.comment, "newly added test comment")
        
    
    def test_can_upvote_suggestion(self):
        """
        Test to check that a user can upvote a feature
        or bug suggestion 
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        logged_in_user_id = User.objects.get(username="testuser").id
        random_suggestion_id = choice(range(1,4))
        self.client.post(reverse("upvote_suggestion", kwargs={"id": random_suggestion_id}))
        retrieved_upvote = Upvote.objects.get(user__id=logged_in_user_id)
        self.assertEqual(retrieved_upvote.suggestion.id, random_suggestion_id)
        
        
    def test_can_upvote_comment(self):
        """
        Test to check that a user can upvote a comment
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        logged_in_user_id = User.objects.get(username="testuser").id
        random_comment_id = choice(range(1,3))
        self.client.post(reverse("upvote_comment", kwargs={"id": random_comment_id}))
        retrieved_upvote = Upvote.objects.get(user__id=logged_in_user_id)
        self.assertEqual(retrieved_upvote.comment.id, random_comment_id)
        
    def test_get_suggestion_admin_page(self):
        """
        Test to check that the view_suggestion page returns a response
        code of 200 and uses the view_feature.html or view_bug.html template.
        Should return a standard view_feature/view_bug page is the logged in user
        is not an admin
        """
        self.client.force_login(User.objects.get_or_create(username="testadminuser", is_staff=True, email="testadminuser@email.com")[0])
        page = self.client.get(reverse("admin_page", kwargs={"id": 1}), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "suggestion_admin_page.html")
        
        self.client.force_login(User.objects.get_or_create(username="testuser",email="testuser@email.com")[0])
        page = self.client.get(reverse("admin_page", kwargs={"id": 1}), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "view_feature.html")
        
        
    def test_can_update_admin_page_values_via_frontend(self):
        """
        Test to check if admin users can update the values on a 
        suggestion admin page
        """
        self.client.force_login(User.objects.get_or_create(username="testadminuser", is_staff=True, email="testadminuser@email.com")[0])
        random_suggestion_id = choice(range(1,4))
        admin_page_values = {"adminPageSubmit": "adminPageSubmit", "status": 2, "priority": 1, "in_current_voting_cycle": True,"github_branch": "test", "suggestion": random_suggestion_id}
        self.client.post(reverse("admin_page", kwargs={"id": random_suggestion_id}), admin_page_values, follow=True)
        
        retrieved_values = SuggestionAdminPage.objects.get(suggestion__id= random_suggestion_id)
        
        self.assertEqual(retrieved_values.status, 2)
        self.assertEqual(retrieved_values.priority, 1)
        self.assertEqual(retrieved_values.github_branch, "test")
        
        
    def test_can_flag_item(self):
        """
        Test to check that a user can flag a comment 
        or suggestion via the frontend url
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        logged_in_user_id = User.objects.get(username="testuser").id
        random_suggestion_id = choice(range(1,4))
        self.client.get(reverse("flag", kwargs={"item_type": 2, "item_id": random_suggestion_id, "reason":1}))
        
        retrieved_values = Flag.objects.get(flagged_by__id=logged_in_user_id)
        
        self.assertEqual(retrieved_values.reason, 1)
        self.assertEqual(retrieved_values.suggestion.id, random_suggestion_id)
        
        random_comment = choice(Comment.objects.all())
        self.client.get(reverse("flag", kwargs={"item_type": 1, "item_id": random_comment.id, "reason":2}))
        
        retrieved_comment_flag_values = Flag.objects.get(flagged_by__id=logged_in_user_id, comment=random_comment)
        self.assertEqual(retrieved_comment_flag_values.reason, 2)
        
        
    def test_get_userpage(self):
        """
        Test to check that the userpage page returns a response
        code of 200 and uses the userpage.html template. Should redirect
        to home if userpage is not the userpage of the logged in user
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        logged_in_user_id = User.objects.get(username="testuser").id
        page = self.client.get(reverse("userpage", kwargs={"user_id": logged_in_user_id}))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "userpage.html")
        
        page = self.client.get(reverse("userpage", kwargs={"user_id": 1}), follow=True)
        self.assertTemplateUsed(page, "home.html")
        
    def test_get_promote_feature_page(self):
        """
        Test to check that the promote_feature page returns a response
        code of 200 and uses the promote_feature.html template. If
        coins are not enabled, should redirect to home
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        page = self.client.get(reverse("promote_feature"), follow=True)
        self.assertEqual(page.status_code, 200)
        if settings.COINS_ENABLED:
            self.assertTemplateUsed(page, "promote_feature.html")
        else:
            self.assertTemplateUsed(page, "home.html")
        
    def test_user_can_promote_feature(self):
        """
        Test to check that a user can promote a feature
        using the frontend promote_feature page. Should only be
        possible if coins are enabled
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        random_feature_suggestion = choice(Suggestion.objects.filter(is_feature=True))
        random_date_within_20_days = (datetime.date.today() + datetime.timedelta(days=choice(range(20))))
        random_promotion_days = choice(range(1,6))
        
        promote_feature_values = {"featureSuggestion": random_feature_suggestion.id, "startDate": random_date_within_20_days, "promotionDays": random_promotion_days}
        
        self.client.post(reverse("promote_feature"), promote_feature_values, follow=True)
        
        if settings.COINS_ENABLED:
        
            retrieved_promotion = PromotedFeatureSuggestion.objects.get(user = User.objects.get(username="testuser"))
            self.assertEqual(retrieved_promotion.start_date, random_date_within_20_days)
            self.assertEqual(random_date_within_20_days + datetime.timedelta(days=random_promotion_days), retrieved_promotion.end_date)

    def test_get_view_data_page(self):
        """
        Test to check that the view_data page returns a response
        code of 200 and uses the view_data.html template. 
        """
        page = self.client.get(reverse("view_data"))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "view_data.html")
        

class TestHelpers(TestCase):
    
    @classmethod
    def setUpTestData(cls):

        user_1 = User(username="Test User")
        user_1.save()
        user_2 = User(username="Another Test User", email="example@email.com")
        user_2.save()
        user_3 = User(username="withpassword", password="password", email="withpassword@email.com")
        user_3.save()
        
        suggestion_1 = Suggestion(is_feature=True, user=user_1, title="Test Suggestion 1", details="Any old detials", delay_submission=False)
        suggestion_1.save()
        suggestion_2 = Suggestion(is_feature=True, user=user_2, title="Test Suggestion 2", details="Any old detials", delay_submission=True)
        suggestion_2.save()
        suggestion_3 = Suggestion.objects.create( is_feature=True, user=user_2, title="Test Suggestion 3", details="Any old detials", delay_submission=False)
        suggestion_3.save()
        suggestion_4 = Suggestion.objects.create( is_feature=True, user=user_1, title="Test Suggestion 4", details="Any old detials", delay_submission=False)
        suggestion_4.save()
        suggestion_5 = Suggestion.objects.create( is_feature=False, user=user_1, title="Test Suggestion 4", details="Any old detials", delay_submission=False)
        suggestion_5.save()
        
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
        admin_page_4 = SuggestionAdminPage(suggestion=suggestion_4,  current_winner=False, in_current_voting_cycle=False)
        admin_page_4.save()
        
        upvote_suggestion_1_1 = Upvote(user=user_1, suggestion= suggestion_1)
        upvote_suggestion_1_1.save()
        upvote_suggestion_2_1 = Upvote(user=user_1, suggestion= suggestion_2)
        upvote_suggestion_2_1.save()
        upvote_suggestion_2_2 = Upvote(user=user_2, suggestion= suggestion_2)
        upvote_suggestion_2_2.save()
        upvote_suggestion_2_3 = Upvote(user=user_1, suggestion= suggestion_2)
        upvote_suggestion_2_3.save()
        
        coins_purchase_1 = CoinsPurchase(name="coins purchase 1", coins_price=200)
        coins_purchase_1.save()
        coins_purchase_2 = CoinsPurchase(name="coins purchase 2", coins_price=500)
        coins_purchase_2.save()
        suggestion_coins_purchase = CoinsPurchase(name="Suggestion", coins_price=500)
        suggestion_coins_purchase.save()
        upvote_coins_purchase = CoinsPurchase(name="Upvote", coins_price=100)
        upvote_coins_purchase.save()
        promote_feature_purchase = CoinsPurchase(name="Feature Suggestion Promotion", coins_price=600)
        promote_feature_purchase.save()
        
        coins_store_item_500= StoreItem(name="500 coins", price=0, delivery_required=False, is_coins=True, coins_amount=500)
        coins_store_item_500.save()
        
        
    def test_can_return_all_current_features_only(self):
        """
        Test to check that return_current_features returns all
        suggestions that are features and in_current_voting_cycle, 
        and none of these features are left out
        """
        returned_features = return_current_features()
        self.assertTrue(len(returned_features)>0)
        for feature in returned_features:
            self.assertTrue(feature.is_feature)
            feature_admin_object = SuggestionAdminPage.objects.get(suggestion=feature)
            self.assertTrue(feature_admin_object.in_current_voting_cycle)
            
        
        all_current_features_admin = SuggestionAdminPage.objects.filter(suggestion__is_feature=True, in_current_voting_cycle=True)
        self.assertEqual(len(all_current_features_admin), len(returned_features))
        
    
    def test_can_sort_featurez(self):
        """
        Test to check that returned features, bugs and comments
        can be sorted correctly
        """
        for i in range(10):
            random_suggestion = choice(Suggestion.objects.all())
            random_user = choice(User.objects.all())
            new_upvote = Upvote(user=random_user, suggestion=random_suggestion)
            new_upvote.save()
            
        for i in range (10):
            random_suggestion = choice(Suggestion.objects.all())
            random_user = choice(User.objects.all())
            new_comment = Comment(user=random_user, suggestion=random_suggestion, comment="test")
            new_comment.save()
            
        for i in range(15):
            random_comment = choice(Comment.objects.all())
            random_user = choice(User.objects.all())
            comment_upvote = Upvote(user=random_user, comment=random_comment)
            comment_upvote.save()
            
        
        most_upvoted_feature_first = return_current_features()
        previous_entry_upvotes = 1000
        for feature in most_upvoted_feature_first:
            self.assertTrue(feature.upvotes <= previous_entry_upvotes)
            previous_entry_upvotes = feature.upvotes
        
        most_upvoted_bug_first = return_all_current_bugs("-upvotes")
        previous_entry_upvotes = 1000
        for bug in most_upvoted_bug_first:
            self.assertTrue(bug.upvotes <= previous_entry_upvotes)
            previous_entry_upvotes = bug.upvotes
            
        most_upvoted_comment_first= return_public_suggestion_comments(choice(Suggestion.objects.all()), "-upvvotes")
        previous_entry_upvotes = 1000
        for comment in most_upvoted_comment_first:
            self.assertTrue(comment.upvotes <= previous_entry_upvotes)
            previous_entry_upvotes = comment.upvotes
            
        oldest_feature_first = return_current_features("oldest")
        previous_entry_date = datetime.date(2050,1,1)
        for feature in oldest_feature_first:
            self.assertTrue(feature.date_time.date() <= previous_entry_date)
            previous_entry_date= feature.date_time.date()
            
            
        oldest_bug_first = return_all_current_bugs("oldest")
        previous_entry_date = datetime.date(2050,1,1)
        for bug in oldest_bug_first:
            self.assertTrue(bug.date_time.date() <= previous_entry_date)
            previous_entry_date= bug.date_time.date()
            
        oldest_comment_first = return_public_suggestion_comments(choice(Suggestion.objects.all()), "oldest")
        previous_entry_date = datetime.date(2050,1,1)
        for comment in oldest_comment_first:
            self.assertTrue(comment.date_time.date() <= previous_entry_date)
            previous_entry_date= comment.date_time.date()
            
            
        newest_feature_first = return_current_features("newest")
        previous_entry_date = datetime.date(1990,1,1)
        for feature in newest_feature_first:
            self.assertTrue(feature.date_time.date() >= previous_entry_date)
            previous_entry_date= feature.date_time.date()
            
            
        newest_bug_first = return_all_current_bugs("newest")
        previous_entry_date = datetime.date(1990,1,1)
        for bug in newest_bug_first:
            self.assertTrue(bug.date_time.date() >= previous_entry_date)
            previous_entry_date= bug.date_time.date()
            
        newest_comment_first = return_public_suggestion_comments(choice(Suggestion.objects.all()), "newest")
        previous_entry_date = datetime.date(1990,1,1)
        for comment in newest_comment_first:
            self.assertTrue(comment.date_time.date() >= previous_entry_date)
            previous_entry_date= comment.date_time.date()
            
            
    def test_can_return_admin_page_comments_only(self):
        """
        Test to check that return_admin_suggestion_comments 
        returns admin page comments only
        """
        
        random_suggestion = choice(Suggestion.objects.all())
        random_user = choice(User.objects.all())
        admin_comment_count = 0
        for i in range(10):
            random_boolean = choice([True, False])
            suggestion_comment = Comment(suggestion=random_suggestion, user=random_user, admin_page_comment=random_boolean)
            suggestion_comment.save()
            if random_boolean == True:
                admin_comment_count += 1
            
        admin_comments = return_admin_suggestion_comments(random_suggestion)
        self.assertEqual(admin_comment_count, len(admin_comments))
        for comment in admin_comments:
            self.assertTrue(comment.admin_page_comment)
            
            
    def test_can_get_userpage_values(self):
        """
        Test that get_userpage_values retrieves a dictionary with 
        the votes, purchases, coin_history, and suggestions for that
        user
        """
        new_user = User(username="userpage user", email="userpage@email.com", password="password")
        new_user.save()
        
        suggestion_1 = Suggestion(is_feature=True, user=new_user, title="Userpage suggestion 1", details="Any old detials", delay_submission=False)
        suggestion_1.save()
        suggestion_2 = Suggestion(is_feature=True, user=new_user, title="Userpage suggestion 2", details="Any old detials")
        suggestion_2.save()
        
        
        for i in range(5):
            random_suggestion = choice(Suggestion.objects.all())
            upvote = Upvote(suggestion=random_suggestion, user=new_user)
            upvote.save()
            
            random_coin_transaction = choice(range(1,10))
            coin_history_entry = UserCoinHistory(user=new_user, coins_change=1, transaction=random_coin_transaction)
            coin_history_entry.save()
            
            order = Order(user=new_user)
            order.save()
            random_store_item = choice(StoreItem.objects.all())
            order_item = OrderItem(order=order, item=random_store_item, quantity=1, total_purchase_price=1)
            order_item.save()
            
        userpage_values = get_userpage_values(new_user)
        
        self.assertEqual(len(userpage_values["coin_history"]), 5)
        
        random_purchase = choice(userpage_values["purchases"])
        self.assertTrue(isinstance(random_purchase, Order))
        random_coin_history = choice(userpage_values["coin_history"])
        self.assertTrue(isinstance(random_coin_history, UserCoinHistory))
        random_vote = choice(userpage_values["votes"])
        self.assertTrue(isinstance(random_vote, Upvote))
        random_suggestion=choice(userpage_values["suggestions"])
        self.assertTrue(isinstance(random_suggestion, Suggestion))
            
            
    def test_get_promoted_features_returns_only_current_promoted_features(self):
        """
        Test to check that get_promoted_features returns only promoted features with 
        a start_date >= today and an endate < today
        """
        random_user = choice(User.objects.all())
        
        yesterday = (datetime.date.today() - datetime.timedelta(days=1))
        today = datetime.date.today()
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1))
        day_after_tomorrow = (datetime.date.today() + datetime.timedelta(days=2))
        
        first_suggestion = Suggestion.objects.get(id=1)
        second_suggestion = Suggestion.objects.get(id=2)
        third_suggestion = Suggestion.objects.get(id=3)
        fourth_suggestion = Suggestion.objects.get(id=4)
        
        starts_yesterday_ends_tomorrow = PromotedFeatureSuggestion(user=random_user, suggestion=first_suggestion, start_date=yesterday, end_date=tomorrow)
        starts_yesterday_ends_tomorrow.save()
        starts_today_ends_tomorrow = PromotedFeatureSuggestion(user=random_user, suggestion=second_suggestion, start_date=today, end_date=tomorrow)
        starts_today_ends_tomorrow.save()
        starts_tomorrow_ends_day_after_tomorrow = PromotedFeatureSuggestion(user=random_user, suggestion=third_suggestion, start_date=tomorrow, end_date=day_after_tomorrow )
        starts_tomorrow_ends_day_after_tomorrow.save()
        starts_yesterday_ends_today = PromotedFeatureSuggestion(user=random_user, suggestion=fourth_suggestion, start_date= yesterday, end_date=today)
        starts_yesterday_ends_today.save()
        
        promoted_features = get_promoted_features()
        
        self.assertTrue(starts_yesterday_ends_tomorrow in promoted_features)
        self.assertTrue(starts_today_ends_tomorrow in promoted_features)
        self.assertFalse(starts_tomorrow_ends_day_after_tomorrow in promoted_features)
        self.assertFalse(starts_yesterday_ends_today in promoted_features)