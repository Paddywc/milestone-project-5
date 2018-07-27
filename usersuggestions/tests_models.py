import datetime
from random import choice

from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import User
from usersuggestions.models import Suggestion, Comment, SuggestionAdminPage, Upvote, Flag, PromotedFeatureSuggestion


class TestModels(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_1 = User(username="Test User")
        user_1.save()
        user_2 = User(username="Another Test User", email="example@email.com")
        user_2.save()

        suggestion_1 = Suggestion(is_feature=True, user=user_1, title="Test Suggestion 1", details="Any old detials",
                                  delay_submission=False)
        suggestion_1.save()
        suggestion_2 = Suggestion(id=2, is_feature=True, user=user_2, title="Test Suggestion 2",
                                  details="Any old detials", delay_submission=True)
        suggestion_2.save()
        suggestion_3 = Suggestion(is_feature=False, user=user_2, title="Test Suggestion 3", details="Any old detials",
                                  delay_submission=False)
        suggestion_3.save()

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

        upvote_suggestion_1_1 = Upvote(user=user_1, suggestion=suggestion_1)
        upvote_suggestion_1_1.save()
        upvote_suggestion_2_1 = Upvote(user=user_1, suggestion=suggestion_2)
        upvote_suggestion_2_1.save()
        upvote_suggestion_2_2 = Upvote(user=user_2, suggestion=suggestion_2)
        upvote_suggestion_2_2.save()
        upvote_suggestion_2_3 = Upvote(user=user_1, suggestion=suggestion_2)
        upvote_suggestion_2_3.save()

    def test_suggestion_suggestion_defaults_as_desired(self):
        """
        Test to check that when creating a Suggestion object, default values
        are assigned as follows: is_feature: False, date_time: now, delay_submission:
        False
        """

        users = User.objects.all()
        random_user = choice(users)

        new_suggestion = Suggestion(title="Testing Defaults", user=random_user)
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
        first_winner.current_winner = True
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

        retrieved_completed_admin_object = SuggestionAdminPage.objects.get(id=random_admin_object.id)
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
        random_user = choice(User.objects.all())
        new_upvote = Upvote(user=random_user)
        new_upvote.save()
        # For this to run, no error has been raised
        self.assertTrue(True)

    def test_flag_defaults_correctly(self):
        """
        Test to check that when creating a Flag object, unspecified values default
        as expected. These are: status : 0, date_time: Now
        """
        random_user = choice(User.objects.all())
        random_comment = choice(Comment.objects.all())

        new_flag = Flag(flagged_item_type=1, flagged_by=random_user,
                        comment=random_comment, reason=2)
        new_flag.save()

        current_date = datetime.date.today()
        self.assertEqual(new_flag.date_time_marked.date(), current_date)
        self.assertEqual(new_flag.result, None)

    def test_creating_flag_requires_item_type_and_user_and_reason(self):
        """
        Test to check that an integrity error is thrown if an attempt
        is made to save a Flag object without a value for flagged_by,
        flagged_item_type and reason
        """

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                random_user = choice(User.objects.all())
                random_suggestion = choice(Suggestion.objects.all())
                without_item_type = Flag(flagged_by=random_user,
                                         suggestion=random_suggestion, reason=2)
                without_item_type.save()

            with transaction.atomic():
                random_suggestion = choice(Suggestion.objects.all())
                without_user = Flag(flagged_item_type=2,
                                    suggestion=random_suggestion, reason=2)
                without_user.save()

            with transaction.atomic():
                random_user = choice(User.objects.all())
                random_comment = choice(Comment.objects.all())
                without_reason = Flag(flagged_item_type=1, flagged_by=random_user,
                                      comment=random_comment)
                without_reason.save()

    def test_flag_choices_appear_as_expected(self):
        """
        Test to check that the human readable values for a Flag's
        choices appear as expected
        """
        random_user = choice(User.objects.all())
        random_suggestion = choice(Suggestion.objects.all())
        new_flag = Flag(flagged_item_type=2, flagged_by=random_user, suggestion=random_suggestion,
                        reason=0)
        new_flag.save()

        self.assertEqual(new_flag.get_flagged_item_type_display(), "suggestion")
        self.assertEqual(new_flag.get_reason_display(), "Spam")

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
                without_user = PromotedFeatureSuggestion(suggestion=random_suggestion, start_date=random_start_date,
                                                         end_date=random_end_date)
                without_user.save()

            with transaction.atomic():
                without_suggestion = PromotedFeatureSuggestion(user=random_user, start_date=random_start_date,
                                                               end_date=random_end_date)
                without_suggestion.save()

            with transaction.atomic():
                without_start_date = PromotedFeatureSuggestion(user=random_user, suggestion=random_suggestion,
                                                               end_date=random_end_date)
                without_start_date.save()

            with transaction.atomic():
                without_end_date = PromotedFeatureSuggestion(user=random_user, suggestion=random_suggestion,
                                                             start_date=random_start_date)
                without_end_date.save()
