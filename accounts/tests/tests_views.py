from random import choice

from django.conf import settings
from django.contrib import auth
from django.test import TestCase
from django.urls import reverse

from market.models import UserCoins
from accounts.models import User


class TestViews(TestCase):

    @classmethod
    def setUpTestData(cls):

        user_1 = User(username="testuser", password="123abc...", email="email@email.com")
        user_1.save()
        user_2 = User(username="anothertestuser", password="456efg...", email="example@email.com")
        user_2.save()
        user_3 = User(username="thirduser", password="123abcefg...", email="withpassword@email.com")
        user_3.save()

        user_1_usercoins = UserCoins(user=user_1, coins=100)
        user_1_usercoins.save()
        user_2_usercoins = UserCoins(user=user_2, coins=500)
        user_2_usercoins.save()
        user_3_usercoins = UserCoins(user=user_3, coins=0)
        user_3_usercoins.save()

    def test_get_signup_page(self):
        """
        Test to check that signup page returns a response
        code of 200 and uses the signup.html template
        """
        page = self.client.get(reverse("signup"), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "signup.html")

    def test_can_signup_using_signup_page(self):
        """
        Test to check that a user can create a new User object 
        from the signup page. If coins are enabled, 100 coins 
        should be added to that user's UserCoins
        """
        form_data = {"username": "signuptester", "email": "signuptester@email.com", "password1": "123abc...",
                     "password2": "123abc..."}
        self.client.post(reverse("signup"), form_data, follow=True)

        new_user = User.objects.get(email="signuptester@email.com")
        if settings.COINS_ENABLED:
            new_user_usercoins = UserCoins.objects.get(user=new_user).coins
            self.assertEqual(new_user_usercoins, 100)

    def test_get_referred_signup_page(self):
        """
        Test to check that referred_signup page returns a 
        response code of 200 and uses the signup.html template
        """
        random_user_id = choice(User.objects.all()).id
        page = self.client.get(reverse("referred_signup", kwargs={"ref_user_id": random_user_id}), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "signup.html")

    def test_creating_referred_user_adds_extra_coins(self):
        """
        Test to check that referred_signup adds 200 usercoins to the 
        user who sent the referral link, and an extra 100 coins to 
        the user who signs up 
        """
        if settings.COINS_ENABLED:
            random_existing_user = choice(User.objects.all())
            existing_users_prior_coins = UserCoins.objects.get(user=random_existing_user).coins

            non_referred_user_data = {"username": "noreferral", "email": "noreferral@email.com",
                                      "password1": "123abc...", "password2": "123abc..."}
            self.client.post(reverse("signup"), non_referred_user_data, follow=True)

            referred_user_data = {"username": "referral", "email": "referral@email.com", "password1": "123abc...",
                                  "password2": "123abc..."}
            self.client.post(reverse("referred_signup", kwargs={"ref_user_id": random_existing_user.id}),
                             referred_user_data, follow=True)

            retrieved_existing_user = User.objects.get(id=random_existing_user.id)
            retrieved_non_referred_user = User.objects.get(email="noreferral@email.com")
            retrieved_referred_user = User.objects.get(email="referral@email.com")

            existing_users_current_coins = UserCoins.objects.get(user=retrieved_existing_user).coins
            self.assertEqual((existing_users_prior_coins + 200), existing_users_current_coins)

            non_referred_user_coins = UserCoins.objects.get(user=retrieved_non_referred_user).coins
            referred_user_coins = UserCoins.objects.get(user=retrieved_referred_user).coins
            self.assertEqual((non_referred_user_coins + 100), referred_user_coins)

    def test_get_login_page(self):
        """
        Test to check that login page returns a response
        code of 200 and uses the login.html template
        """
        page = self.client.get(reverse("login"), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "login.html")

    def test_logout_url_logs_out_user(self):
        """
        Test to check that logout logs out the 
        current user
        """
        self.client.force_login(User.objects.get_or_create(username="logoutuser", email="logoutuser@email.com")[0])
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.client.get(reverse("logout"), follow=True)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
