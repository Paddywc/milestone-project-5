import datetime
from random import choice

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from market.models import CoinsPurchase, StoreItem
from usersuggestions.models import Suggestion, Comment, SuggestionAdminPage, Upvote, Flag, PromotedFeatureSuggestion


class TestViews(TestCase):

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
        suggestion_2 = Suggestion(id=2, is_feature=True, user=user_2, title="Test Suggestion 2",
                                  details="Any old details", delay_submission=True)
        suggestion_2.save()
        suggestion_3 = Suggestion.objects.create(is_feature=False, user=user_2, title="Test Suggestion 3",
                                                 details="Any old details", delay_submission=False)
        suggestion_3.save()

        comment_1 = Comment(user=user_1, suggestion=suggestion_2, comment="test comment")
        comment_1.save()
        comment_2 = Comment(user=user_2, suggestion=suggestion_2, comment="test comment")
        comment_2.save()

        admin_page_1 = SuggestionAdminPage(suggestion=suggestion_2, current_winner=False)
        admin_page_1.save()
        admin_page_2 = SuggestionAdminPage(suggestion=suggestion_1, current_winner=True,
                                           expected_completion_date=datetime.date(2019, 2, 8))
        admin_page_2.save()
        admin_page_3 = SuggestionAdminPage(suggestion=suggestion_3, current_winner=False)
        admin_page_3.save()

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
        Test to check that a new Suggestion object is successfuly created
        on completion of the form
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])

        logged_in_user_id = User.objects.get(username="testuser").id

        form_data = {"is_feature": True, "title": "post suggestion", "details": "some details",
                     "user": logged_in_user_id}
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
        response = self.client.post(reverse("add_suggestion"),
                                    {"purchaseCoins": "purchaseCoins", "purchaseCoinsSelect": 1}, follow=True)
        self.assertTemplateUsed(response, "pay.html")

    def test_form_values_saved_in_session_on_redirect_from_add_suggestion_page(self):
        """
        Test to check that the SuggestionForm values are saved in the session
        if redirected from add_suggestion page to pay page
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        self.client.post(reverse("add_suggestion"),
                         {"purchaseCoins": "purchaseCoins", "purchaseCoinsSelect": 1, "title": "test title",
                          "details": "test details"}, follow=True)
        session = self.client.session
        self.assertEqual(session["session_url"], "http://testserver/suggestions/add/")
        self.assertEqual(session["form_title"], "test title")
        self.assertEqual(session["form_details"], "test details")

    def test_get_issue_tracker_page(self):
        """
        Test to check that the issue_tracker page returns a response
        code of 200 and uses the issue_tracker.html template
        """
        page = self.client.get(reverse("issue_tracker"))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "issue_tracker.html")

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
        comment_values = {"postComment": "postComment", "user": logged_in_user_id, "suggestion": 1,
                          "comment": "newly added test comment"}
        self.client.post(reverse("view_suggestion", kwargs={"id": 1}), comment_values, follow=True)

        retrieved_comment = Comment.objects.get(user__id=logged_in_user_id)
        self.assertEqual(retrieved_comment.comment, "newly added test comment")

    def test_can_upvote_suggestion(self):
        """
        Test to check that a user can upvote a feature
        or bug suggestion
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        logged_in_user_id = User.objects.get(username="testuser").id
        random_suggestion_id = choice(range(1, 4))
        self.client.post(reverse("upvote_suggestion", kwargs={"id": random_suggestion_id}))
        retrieved_upvote = Upvote.objects.get(user__id=logged_in_user_id)
        self.assertEqual(retrieved_upvote.suggestion.id, random_suggestion_id)

    def test_can_upvote_comment(self):
        """
        Test to check that a user can upvote a comment
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        logged_in_user_id = User.objects.get(username="testuser").id
        random_comment_id = choice(range(1, 3))
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
        self.client.force_login(
            User.objects.get_or_create(username="testadminuser", is_staff=True, email="testadminuser@email.com")[0])
        page = self.client.get(reverse("admin_page", kwargs={"id": 1}), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "suggestion_admin_page.html")

        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        page = self.client.get(reverse("admin_page", kwargs={"id": 1}), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "view_feature.html")

    def test_can_update_admin_page_values_via_frontend(self):
        """
        Test to check if admin users can update the values on a
        suggestion admin page
        """
        self.client.force_login(
            User.objects.get_or_create(username="testadminuser", is_staff=True, email="testadminuser@email.com")[0])
        random_suggestion_id = choice(range(1, 4))
        admin_page_values = {"adminPageSubmit": "adminPageSubmit", "status": 2, "priority": 1,
                             "in_current_voting_cycle": True, "github_branch": "test",
                             "suggestion": random_suggestion_id}
        self.client.post(reverse("admin_page", kwargs={"id": random_suggestion_id}), admin_page_values, follow=True)

        retrieved_values = SuggestionAdminPage.objects.get(suggestion__id=random_suggestion_id)

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
        random_suggestion_id = choice(range(1, 4))
        self.client.get(reverse("flag", kwargs={"item_type": 2, "item_id": random_suggestion_id, "reason": 1}))

        retrieved_values = Flag.objects.get(flagged_by__id=logged_in_user_id)

        self.assertEqual(retrieved_values.reason, 1)
        self.assertEqual(retrieved_values.suggestion.id, random_suggestion_id)

        random_comment = choice(Comment.objects.all())
        self.client.get(reverse("flag", kwargs={"item_type": 1, "item_id": random_comment.id, "reason": 2}))

        retrieved_comment_flag_values = Flag.objects.get(flagged_by__id=logged_in_user_id, comment=random_comment)
        self.assertEqual(retrieved_comment_flag_values.reason, 2)

    def test_get_promote_feature_page(self):
        """
        Test to check that the promote_feature page returns a response
        code of 200 and uses the promote_feature.html template. If
        coins are not enabled, should redirect to issue_tracker
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        page = self.client.get(reverse("promote_feature"), follow=True)
        self.assertEqual(page.status_code, 200)
        if settings.COINS_ENABLED:
            self.assertTemplateUsed(page, "promote_feature.html")
        else:
            self.assertTemplateUsed(page, "issue_tracker.html")

    def test_user_can_promote_feature(self):
        """
        Test to check that a user can promote a feature
        using the frontend promote_feature page. Should only be
        possible if coins are enabled
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])
        random_feature_suggestion = choice(Suggestion.objects.filter(is_feature=True))
        random_date_within_20_days = (datetime.date.today() + datetime.timedelta(days=choice(range(20))))
        random_promotion_days = choice(range(1, 6))

        promote_feature_values = {"featureSuggestion": random_feature_suggestion.id,
                                  "startDate": random_date_within_20_days, "promotionDays": random_promotion_days}

        self.client.post(reverse("promote_feature"), promote_feature_values, follow=True)

        if settings.COINS_ENABLED:
            retrieved_promotion = PromotedFeatureSuggestion.objects.get(user=User.objects.get(username="testuser"))
            self.assertEqual(retrieved_promotion.start_date, random_date_within_20_days)
            self.assertEqual(random_date_within_20_days + datetime.timedelta(days=random_promotion_days),
                             retrieved_promotion.end_date)

    def test_get_view_data_page(self):
        """
        Test to check that the view_data page returns a response
        code of 200 and uses the view_data.html template.
        """
        page = self.client.get(reverse("view_data"))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "view_data.html")
