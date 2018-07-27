import datetime
from random import choice

from django.test import TestCase

from accounts.models import User
from market.models import CoinsPurchase, StoreItem, UserCoinHistory, Order, OrderItem
from usersuggestions.helpers import return_current_features, return_all_current_bugs, return_public_suggestion_comments, \
    return_admin_suggestion_comments, get_userpage_values, get_promoted_features
from usersuggestions.models import Suggestion, Comment, SuggestionAdminPage, Upvote, PromotedFeatureSuggestion


class TestHelpers(TestCase):

    @classmethod
    def setUpTestData(cls):

        user_1 = User(username="Test User")
        user_1.save()
        user_2 = User(username="Another Test User", email="example@email.com")
        user_2.save()
        user_3 = User(username="withpassword", password="password", email="withpassword@email.com")
        user_3.save()

        suggestion_1 = Suggestion(is_feature=True, user=user_1, title="Test Suggestion 1", details="Any old detials",
                                  delay_submission=False)
        suggestion_1.save()
        suggestion_2 = Suggestion(is_feature=True, user=user_2, title="Test Suggestion 2", details="Any old detials",
                                  delay_submission=True)
        suggestion_2.save()
        suggestion_3 = Suggestion.objects.create(is_feature=True, user=user_2, title="Test Suggestion 3",
                                                 details="Any old detials", delay_submission=False)
        suggestion_3.save()
        suggestion_4 = Suggestion.objects.create(is_feature=True, user=user_1, title="Test Suggestion 4",
                                                 details="Any old detials", delay_submission=False)
        suggestion_4.save()
        suggestion_5 = Suggestion.objects.create(is_feature=False, user=user_1, title="Test Suggestion 4",
                                                 details="Any old detials", delay_submission=False)
        suggestion_5.save()

        comment_1 = Comment(user=user_1, suggestion=suggestion_2, comment="test comment")
        comment_1.save()
        comment_2 = Comment(user=user_2, suggestion=suggestion_2, comment="test comment")
        comment_2.save()

        admin_page_1 = SuggestionAdminPage(suggestion=suggestion_2, current_winner=False)
        admin_page_1.save()
        admin_page_2 = SuggestionAdminPage(suggestion=suggestion_1, current_winner=False)
        admin_page_2.save()
        admin_page_3 = SuggestionAdminPage(suggestion=suggestion_3, current_winner=False)
        admin_page_3.save()
        admin_page_4 = SuggestionAdminPage(suggestion=suggestion_4, current_winner=False, in_current_voting_cycle=False)
        admin_page_4.save()

        upvote_suggestion_1_1 = Upvote(user=user_1, suggestion=suggestion_1)
        upvote_suggestion_1_1.save()
        upvote_suggestion_2_1 = Upvote(user=user_1, suggestion=suggestion_2)
        upvote_suggestion_2_1.save()
        upvote_suggestion_2_2 = Upvote(user=user_2, suggestion=suggestion_2)
        upvote_suggestion_2_2.save()
        upvote_suggestion_2_3 = Upvote(user=user_1, suggestion=suggestion_2)
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

        coins_store_item_500 = StoreItem(name="500 coins", price=0, delivery_required=False, is_coins=True,
                                         coins_amount=500)
        coins_store_item_500.save()

    def test_can_return_all_current_features_only(self):
        """
        Test to check that return_current_features returns all
        suggestions that are features and in_current_voting_cycle,
        and none of these features are left out
        """
        returned_features = return_current_features()
        self.assertTrue(len(returned_features) > 0)
        for feature in returned_features:
            self.assertTrue(feature.is_feature)
            feature_admin_object = SuggestionAdminPage.objects.get(suggestion=feature)
            self.assertTrue(feature_admin_object.in_current_voting_cycle)

        all_current_features_admin = SuggestionAdminPage.objects.filter(suggestion__is_feature=True,
                                                                        in_current_voting_cycle=True)
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

        for i in range(10):
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

        most_upvoted_comment_first = return_public_suggestion_comments(choice(Suggestion.objects.all()), "-upvvotes")
        previous_entry_upvotes = 1000
        for comment in most_upvoted_comment_first:
            self.assertTrue(comment.upvotes <= previous_entry_upvotes)
            previous_entry_upvotes = comment.upvotes

        oldest_feature_first = return_current_features("oldest")
        previous_entry_date = datetime.date(2050, 1, 1)
        for feature in oldest_feature_first:
            self.assertTrue(feature.date_time.date() <= previous_entry_date)
            previous_entry_date = feature.date_time.date()

        oldest_bug_first = return_all_current_bugs("oldest")
        previous_entry_date = datetime.date(2050, 1, 1)
        for bug in oldest_bug_first:
            self.assertTrue(bug.date_time.date() <= previous_entry_date)
            previous_entry_date = bug.date_time.date()

        oldest_comment_first = return_public_suggestion_comments(choice(Suggestion.objects.all()), "oldest")
        previous_entry_date = datetime.date(2050, 1, 1)
        for comment in oldest_comment_first:
            self.assertTrue(comment.date_time.date() <= previous_entry_date)
            previous_entry_date = comment.date_time.date()

        newest_feature_first = return_current_features("newest")
        previous_entry_date = datetime.date(1990, 1, 1)
        for feature in newest_feature_first:
            self.assertTrue(feature.date_time.date() >= previous_entry_date)
            previous_entry_date = feature.date_time.date()

        newest_bug_first = return_all_current_bugs("newest")
        previous_entry_date = datetime.date(1990, 1, 1)
        for bug in newest_bug_first:
            self.assertTrue(bug.date_time.date() >= previous_entry_date)
            previous_entry_date = bug.date_time.date()

        newest_comment_first = return_public_suggestion_comments(choice(Suggestion.objects.all()), "newest")
        previous_entry_date = datetime.date(1990, 1, 1)
        for comment in newest_comment_first:
            self.assertTrue(comment.date_time.date() >= previous_entry_date)
            previous_entry_date = comment.date_time.date()

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
            suggestion_comment = Comment(suggestion=random_suggestion, user=random_user,
                                         admin_page_comment=random_boolean)
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
        the votes, purchases, coin_history, and SuggestionAdminPages
        for that user
        """
        new_user = User(username="userpage user", email="userpage@email.com", password="password")
        new_user.save()

        suggestion_1 = Suggestion(is_feature=True, user=new_user, title="Userpage suggestion 1",
                                  details="Any old detials", delay_submission=False)
        suggestion_1.save()
        suggestion_2 = Suggestion(is_feature=True, user=new_user, title="Userpage suggestion 2",
                                  details="Any old detials")
        suggestion_2.save()
        
        suggestion_admin_1 = SuggestionAdminPage(suggestion=suggestion_1)
        suggestion_admin_1.save()
        suggestion_admin_2 = SuggestionAdminPage(suggestion= suggestion_2)
        suggestion_admin_2.save()

        for i in range(5):
            random_suggestion = choice(Suggestion.objects.all())
            upvote = Upvote(suggestion=random_suggestion, user=new_user)
            upvote.save()

            random_coin_transaction = choice(range(1, 10))
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
        random_suggestion_admin = choice(userpage_values["suggestions"])
        self.assertTrue(isinstance(random_suggestion_admin, SuggestionAdminPage))

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

        starts_yesterday_ends_tomorrow = PromotedFeatureSuggestion(user=random_user, suggestion=first_suggestion,
                                                                   start_date=yesterday, end_date=tomorrow)
        starts_yesterday_ends_tomorrow.save()
        starts_today_ends_tomorrow = PromotedFeatureSuggestion(user=random_user, suggestion=second_suggestion,
                                                               start_date=today, end_date=tomorrow)
        starts_today_ends_tomorrow.save()
        starts_tomorrow_ends_day_after_tomorrow = PromotedFeatureSuggestion(user=random_user,
                                                                            suggestion=third_suggestion,
                                                                            start_date=tomorrow,
                                                                            end_date=day_after_tomorrow)
        starts_tomorrow_ends_day_after_tomorrow.save()
        starts_yesterday_ends_today = PromotedFeatureSuggestion(user=random_user, suggestion=fourth_suggestion,
                                                                start_date=yesterday, end_date=today)
        starts_yesterday_ends_today.save()

        promoted_features = get_promoted_features()

        self.assertTrue(starts_yesterday_ends_tomorrow in promoted_features)
        self.assertTrue(starts_today_ends_tomorrow in promoted_features)
        self.assertFalse(starts_tomorrow_ends_day_after_tomorrow in promoted_features)
        self.assertFalse(starts_yesterday_ends_today in promoted_features)
