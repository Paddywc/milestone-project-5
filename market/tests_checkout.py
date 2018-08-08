from importlib import import_module
from random import choice

from django.conf import settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import transaction
from django.http import HttpRequest
from django.test import TestCase
from stripe import AuthenticationError

from accounts.models import User
from market.checkout import process_stripe_payment, process_order, cart_contains_item_needing_delivery
from market.models import UserCoins, CoinsPurchase, StoreItem, Order, OrderItem
from market.views import cart_add
from usersuggestions.models import Suggestion


class TestCheckout(TestCase):

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
        non_coins_store_item_2 = StoreItem(name="not coins 2", price=10, delivery_required=True, is_coins=False)
        non_coins_store_item_2.save()
        non_coins_store_item_3 = StoreItem(name="not coins 3", price=99, delivery_required=True, is_coins=False)
        non_coins_store_item_3.save()

        order_1 = Order(user=user_1)
        order_1.save()
        order_2 = Order(user=user_2)
        order_2.save()
        order_3 = Order(user=user_3)
        order_3.save()

    def test_valid_stripe_api_key_and_token_required_to_process_payment(self):
        """
        Test to check that process_stripe_payment requires a valid
        stripe api key and stripe token, otherwise it should throw an authentication
        error
        """

        random_store_item = choice(StoreItem.objects.exclude(price=0))

        # below block of code from: https://stackoverflow.com/questions/16865947/django-httprequest-object-has-no-attribute-session
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)

        # below two lines of code from https://stackoverflow.com/questions/11938164/why-dont-my-django-unittests-know-that-messagemiddleware-is-installed
        # fixes bug where test fails because unittest
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        cart_add(request, random_store_item.id)

        request.POST["stripeToken"] = "tok_visa_debit"

        process_stripe_payment(request)

        with self.assertRaises(AuthenticationError):
            with transaction.atomic():
                settings.STRIPE_SECRET = "An invalid secret"
                process_stripe_payment(request)

            with transaction.atomic():
                request.POST["stripeToken"] = "an invalid token"
                process_stripe_payment(request)

    def test_process_order_adds_coins_to_users_account_if_coins_in_order(self):
        """
        Test to check that if coins are in the cart, process_order will add
        that amount of coins to the user's UserCoins row
        """
        self.client.force_login(User.objects.get_or_create(username="coinsuser", email="coinsuser@email.com")[0])

        current_user = User.objects.get(username="coinsuser")

        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)

        # below two lines of code from https://stackoverflow.com/questions/11938164/why-dont-my-django-unittests-know-that-messagemiddleware-is-installed
        # fixes bug where test fails because unitest
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        random_coins_store_item = choice(StoreItem.objects.filter(is_coins=True))
        cart_add(request, random_coins_store_item.id)

        process_order(request, current_user)

        current_users_coins = UserCoins.objects.get(user=current_user).coins
        self.assertEqual(current_users_coins, random_coins_store_item.coins_amount)

    def test_process_order_adds_creates_order_with_all_items_in_cart(self):
        """
        Test to check that process_order creates an Order object. It should also
        create an OrderItem object for each item in the cart, linked to the Order object
        via a foreign key. Quantity value should match the quantity of the item in the cart
        """

        self.client.force_login(User.objects.get_or_create(username="orderuser", email="orderuser@email.com")[0])

        current_user = User.objects.get(username="orderuser")

        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)

        first_item = choice(StoreItem.objects.all())
        second_item = choice(StoreItem.objects.exclude(id=first_item.id))

        # below two lines of code from https://stackoverflow.com/questions/11938164/why-dont-my-django-unittests-know-that-messagemiddleware-is-installed
        # fixes bug where test fails because unittest
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        cart_add(request, first_item.id)
        cart_add(request, first_item.id)
        cart_add(request, second_item.id)

        process_order(request, current_user)

        retrieved_order = Order.objects.get(user=current_user)
        retrieved_first_item = OrderItem.objects.get(order__user=current_user, item=first_item)
        retrieved_second_item = OrderItem.objects.get(order__user=current_user, item=second_item)

        self.assertEqual(retrieved_first_item.order, retrieved_order)
        self.assertEqual(retrieved_second_item.order, retrieved_order)
        self.assertEqual(retrieved_first_item.quantity, 2)
        self.assertEqual(retrieved_second_item.quantity, 1)
        self.assertEqual(retrieved_first_item.total_purchase_price, (retrieved_first_item.item.price * 2))
        self.assertEqual(retrieved_second_item.total_purchase_price, retrieved_second_item.item.price)

    def test_can_check_if_cart_has_item_needing_delivery(self):
        """
        Test to check that cart_contains_item_needing_delivery returns
        True if the cart has at least one item with a delivery_required
        value of True, returns False otherwise
        """

        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)

        # below two lines of code from https://stackoverflow.com/questions/11938164/why-dont-my-django-unittests-know-that-messagemiddleware-is-installed
        # fixes bug where test fails because unittest
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        random_non_delivery_item_1 = choice(StoreItem.objects.filter(delivery_required=False))
        random_non_delivery_item_2 = choice(
            StoreItem.objects.filter(delivery_required=False).exclude(id=random_non_delivery_item_1.id))
        random_delivery_item = choice(StoreItem.objects.filter(delivery_required=True))

        cart_add(request, random_non_delivery_item_1.id)
        self.assertFalse(cart_contains_item_needing_delivery(request))
        cart_add(request, random_non_delivery_item_2.id)
        self.assertFalse(cart_contains_item_needing_delivery(request))
        cart_add(request, random_delivery_item.id)
        self.assertTrue(cart_contains_item_needing_delivery(request))
