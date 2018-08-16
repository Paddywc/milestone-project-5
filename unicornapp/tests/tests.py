from random import choice

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from market.models import CoinsPurchase, StoreItem, UserCoinHistory, Order, OrderItem
from unicornapp.views import get_userpage_values
from usersuggestions.models import Suggestion, Comment, SuggestionAdminPage, Upvote


class TestUnicornApp(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_1 = User(username="Test User")
        user_1.save()
        user_2 = User(username="Another Test User", email="example@email.com")
        user_2.save()
        user_3 = User(username="withpassword", password="password", email="withpassword@email.com")
        user_3.save()

        suggestion_1 = Suggestion(is_feature=True, user=user_1, title="Test Suggestion 1", details="Any old details",
                                  delay_submission=False)
        suggestion_1.save()
        suggestion_2 = Suggestion(is_feature=True, user=user_2, title="Test Suggestion 2", details="Any old details",
                                  delay_submission=True)
        suggestion_2.save()
        suggestion_3 = Suggestion.objects.create(is_feature=True, user=user_2, title="Test Suggestion 3",
                                                 details="Any old details", delay_submission=False)
        suggestion_3.save()
        suggestion_4 = Suggestion.objects.create(is_feature=True, user=user_1, title="Test Suggestion 4",
                                                 details="Any old details", delay_submission=False)
        suggestion_4.save()

        comment_1 = Comment(user=user_1, suggestion=suggestion_2, comment="test comment")
        comment_1.save()
        comment_2 = Comment(user=user_2, suggestion=suggestion_2, comment="test comment")
        comment_2.save()

        admin_page_1 = SuggestionAdminPage(suggestion=suggestion_2, current_winner=False)
        admin_page_1.save()
        admin_page_2 = SuggestionAdminPage(suggestion=suggestion_1, current_winner=True)
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

    def test_get_userpage(self):
        """
        Test to check that the userpage page returns a response
        code of 200 and uses the userpage.html template. Should redirect
        to issue_tracker if userpage is not the userpage of the logged in user
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        logged_in_user_id = User.objects.get(username="testuser").id
        page = self.client.get(reverse("userpage", kwargs={"user_id": logged_in_user_id}))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "userpage.html")

        page = self.client.get(reverse("userpage", kwargs={"user_id": 1}), follow=True)
        self.assertTemplateUsed(page, "issue_tracker.html")

    def test_can_get_userpage_values(self):
        """
        Test that get_userpage_values retrieves a dictionary with
        the votes, purchases, coin_history, and SuggestionAdminPages
        for that user
        """
        new_user = User(username="userpage user", email="userpage@email.com", password="password")
        new_user.save()

        suggestion_1 = Suggestion(is_feature=True, user=new_user, title="Userpage suggestion 1",
                                  details="Any old details", delay_submission=False)
        suggestion_1.save()
        suggestion_2 = Suggestion(is_feature=True, user=new_user, title="Userpage suggestion 2",
                                  details="Any old details")
        suggestion_2.save()

        suggestion_admin_1 = SuggestionAdminPage(suggestion=suggestion_1)
        suggestion_admin_1.save()
        suggestion_admin_2 = SuggestionAdminPage(suggestion=suggestion_2)
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

    def test_get_home(self):
        """
        Test to check that the home page returns a response
        code of 200 and uses the home.html template.
        """
        page = self.client.get(reverse("home"))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "home.html")
