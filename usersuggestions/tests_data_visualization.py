from random import choice

from django.test import TestCase

import datetime

from usersuggestions.models import Suggestion, Comment, SuggestionAdminPage, Upvote, PromotedFeatureSuggestion
from market.models import CoinsPurchase, StoreItem, UserCoinHistory
from accounts.models import User

from .data_visualization import get_highest_vote_totals, get_coin_expenditures, get_data_for_june_completions_chart

class TestDataVisualization(TestCase):

    @classmethod
    def setUpTestData(cls):
        
        user_1 = User(username="Test User")
        user_1.save()
        user_2 = User(username="Another Test User", email="example@email.com")
        user_2.save()
        user_3 = User(username="withpassword", password="password", email="withpassword@email.com")
        user_3.save()

        for i in range(15):
            
            suggestion = Suggestion(is_feature=True, user=user_1, title="For populating chart", details="Blah blah blah ")
            suggestion.save()
            random_day_in_june = choice(range(1,31))
            date_completed = datetime.date(2018, 6, random_day_in_june)
            admin_page = SuggestionAdminPage(suggestion=suggestion, date_completed=date_completed)
            admin_page.save()
            
        for i in range(40):
            random_suggestion= choice(Suggestion.objects.all())
            upvote =  Upvote(user=user_2, suggestion=random_suggestion )
            upvote.save()
            
        for i in range(10):
            bug = Suggestion(is_feature=False, user=user_1, title="For populating chart", details="Blah blah blah ")
            bug.save()
            random_day_in_june = choice(range(1,31))
            date_completed = datetime.date(2018, 6, random_day_in_june)
            admin_page = SuggestionAdminPage(suggestion=bug, date_completed=date_completed)
            admin_page.save()
        
        for i in range(30):
            random_coin_transaction = choice([1,2,9,3])
            coin_history_entry = UserCoinHistory(user=user_1, coins_change=(0-random_coin_transaction),  transaction=random_coin_transaction)
            coin_history_entry.save()
            
    def test_can_get_highest_vote_total(self):
        """
        Test to check that get_highest_vote_totals returns
        Suggestion objects that are ordered by upvotes. Should
        be the length of the argument
        """
        
        limit = choice(range(1,8))
        totals =get_highest_vote_totals(limit)
        
        self.assertEqual(limit, len(totals))
        
        previous_entry_upvotes = 1000
        for suggestion in totals:
            self.assertTrue(suggestion.upvotes <= previous_entry_upvotes)
            self.assertTrue(isinstance(suggestion, Suggestion))
            previous_entry_upvotes = suggestion.upvotes
            
        
    def test_can_get_coin_expenditures(self):
        """
        Test to check that get_coin_expenditures returns
        that total coins spent on submissions, upvoting, and 
        promoting suggestions
        """
        # Number = the cost used when creating the table
        total_spent_on_submissions = (1 * len(UserCoinHistory.objects.filter(transaction=1)))
        total_spent_on_upvotes = (2 * len(UserCoinHistory.objects.filter(transaction=2)))
        total_spent_on_promoting = (9 * len(UserCoinHistory.objects.filter(transaction=9)))
        
        expenditures = get_coin_expenditures()
        
        self.assertEqual(total_spent_on_submissions, expenditures["submissions"])
        self.assertEqual(total_spent_on_upvotes, expenditures["upvoting"])
        self.assertEqual(total_spent_on_promoting, expenditures["promoting_suggestion"])
        
    def test_can_get_features_and_bugs_completed_each_day_in_june(self):
        """
        Test to check that get_data_for_june_completions_chart returns a dictionary with 
        lists of the total amount of bugs and features completed each day in June 2018
        """
        
        returned_data = get_data_for_june_completions_chart()
        bugs_completed  = returned_data["bug_june_day_counts"]
        features_completed = returned_data["feature_june_day_counts"]
        
        all_features  = Suggestion.objects.filter(is_feature=True)
        all_bugs = Suggestion.objects.filter(is_feature=False)
        
        self.assertEqual(len(all_bugs), sum(bugs_completed))
        self.assertEqual(len(all_features), sum(features_completed))
        
        for suggestion_admin_page in SuggestionAdminPage.objects.all():
            day_of_june_completed = suggestion_admin_page.date_completed.day
            self.assertTrue((bugs_completed[day_of_june_completed-1] >0) or (features_completed[day_of_june_completed-1] > 0))