from importlib import import_module
from random import choice

from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from market.cart import Cart
from market.models import UserCoins, CoinsPurchase, StoreItem, Delivery
from market.views import cart_add, cart_remove
from usersuggestions.models import Suggestion


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
        suggestion_2 = Suggestion(is_feature=True, user=user_2, title="Test Suggestion 2", details="Any old details",
                                  delay_submission=True)
        suggestion_2.save()
        suggestion_3 = Suggestion.objects.create(is_feature=True, user=user_2, title="Test Suggestion 3",
                                                 details="Any old details", delay_submission=False)
        suggestion_3.save()

        user_1_usercoins = UserCoins(user=user_1, coins=100)
        user_1_usercoins.save()
        user_2_usercoins = UserCoins(user=user_2, coins=500)
        user_2_usercoins.save()
        user_3_usercoins = UserCoins(user=user_3, coins=0)
        user_3_usercoins.save()

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
        coins_store_item_200 = StoreItem(name="200 coins", price=2, delivery_required=False, is_coins=True,
                                         coins_amount=200)
        coins_store_item_200.save()
        coins_store_item_1000 = StoreItem(name="1000 coins", price=10, delivery_required=False, is_coins=True,
                                          coins_amount=1000)
        coins_store_item_1000.save()

        non_coins_store_item = StoreItem(name="not coins", price=5, delivery_required=True, is_coins=False)
        non_coins_store_item.save()

    def test_get_store_page(self):
        """
        Test to check that the store page returns a response
        code of 200 and uses the store.html template
        """
        page = self.client.get(reverse("store"), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "store.html")

    def test_can_add_and_remove_cart_item(self):
        """
        Test to check that a user can add and remove
        items from their cart via the frontend url
        """
        random_store_item = choice(StoreItem.objects.all())

        # four lines of code below from: https://stackoverflow.com/questions/16865947/django-httprequest-object-has-no-attribute-session
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)

        # below two lines of code from https://stackoverflow.com/questions/11938164/why-dont-my-django-unittests-know-that-messagemiddleware-is-installed
        # fixes bug where test fails because unittest
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        cart_add(request, random_store_item.id)
        cart = Cart(request)

        self.assertEqual(len(cart), 1)
        self.assertEqual(cart.get_total_price(), random_store_item.price)

        cart_add(request, random_store_item.id)
        cart = Cart(request)

        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.get_total_price(), (random_store_item.price * 2))

        cart_remove(request, random_store_item.id)
        cart = Cart(request)

        self.assertEqual(len(cart), 1)
        self.assertEqual(cart.get_total_price(), random_store_item.price)

    def test_get_view_cart_page(self):
        """
        Test to check that the view_suggestion page returns a response
        code of 200 and uses the cart.html template
        """
        page = self.client.get(reverse("view_cart"), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "cart.html")

    def test_delivery_added_when_form_posted(self):
        """
        Test to check that a new Delivery object is successfully created
        on completion of the form. Should then redirect to pay page
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])

        logged_in_user_id = User.objects.get(username="testuser").id

        form_data = {"user": logged_in_user_id, "full_name": "I'm a test", "phone_number": 424242424242,
                     "street_address_1": "123 Fake Street", "postcode": "10001",
                     "town_or_city": "Springfield", "county": "Dublin", "country": "AU"}

        response = self.client.post(reverse("delivery"), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        retrieved_delivery = Delivery.objects.get(full_name="I'm a test")
        self.assertEqual(retrieved_delivery.phone_number, "424242424242")
        self.assertEqual(retrieved_delivery.country, "AU")
        self.assertEqual(retrieved_delivery.town_or_city, "Springfield")
        self.assertEqual(retrieved_delivery.street_address_1, "123 Fake Street")
        self.assertEqual(retrieved_delivery.postcode, "10001")
        self.assertEqual(retrieved_delivery.current_delivery_method, True)
        self.assertTemplateUsed("pay.html")

    def test_can_only_have_one_current_delivery_address(self):
        """
        Test to check that once a Delivery object's current_delivery_method
        is set to True, all other Delivery objects with that user's foreign
        key have current_delivery_method set to False. If a user adds a delivery
        address via the frontend form, it should automatically become the current_delivery_method
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])

        logged_in_user = User.objects.get(username="testuser")

        form_data = {"user": logged_in_user.id, "full_name": "test 1", "phone_number": 424242424242,
                     "street_address_1": "123 Fake Street", "postcode": "10001",
                     "town_or_city": "Springfield", "county": "Dublin", "country": "AU"}

        self.client.post(reverse("delivery"), form_data, follow=True)
        retrieved_delivery_1 = Delivery.objects.get(full_name="test 1")
        self.assertTrue(retrieved_delivery_1.current_delivery_method)

        form_data["full_name"] = "test 2"
        self.client.post(reverse("delivery"), form_data, follow=True)
        retrieved_delivery_2 = Delivery.objects.get(full_name="test 2")
        self.assertTrue(retrieved_delivery_2.current_delivery_method)

        retrieved_delivery_1 = Delivery.objects.get(full_name="test 1")
        self.assertFalse(retrieved_delivery_1.current_delivery_method)

        retrieved_delivery_1.current_delivery_method = True
        retrieved_delivery_1.save()
        retrieved_delivery_2 = Delivery.objects.get(full_name="test 2")
        self.assertFalse(retrieved_delivery_2.current_delivery_method)

    def test_get_pay_page(self):
        """
        Test to check that the pay page returns a response
        code of 200 and uses the pay.html template. If user has
        no items in their cart, then they should be redirected to the
        store page
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])

        page = self.client.get(reverse("pay"), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "store.html")

        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)

        random_store_item = choice(StoreItem.objects.all())

        # below two lines of code from https://stackoverflow.com/questions/11938164/why-dont-my-django-unittests-know-that-messagemiddleware-is-installed
        # fixes bug where test fails because unitest
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        cart_add(request, random_store_item.id)

        page = self.client.get(reverse("pay"), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "store.html")

    def test_get_earn_coins_page(self):
        """
        Test to check that the earn_coins page returns a response
        code of 200 and uses the earn_coins.html template
        """
        self.client.force_login(User.objects.get_or_create(username="testuser", email="testuser@email.com")[0])

        page = self.client.get(reverse("earn_coins"), follow=True)
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, "earn_coins.html")
