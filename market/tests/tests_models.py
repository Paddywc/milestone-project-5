import datetime
from random import choice

from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import User
from market.models import UserCoins, CoinsPurchase, StoreItem, Order, OrderItem, UserCoinHistory
from usersuggestions.models import Suggestion


class TestModels(TestCase):
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

        order_1 = Order(user=user_1)
        order_1.save()
        order_2 = Order(user=user_2)
        order_2.save()
        order_3 = Order(user=user_3)
        order_3.save()

    def test_store_item_defaults_as_desired(self):
        """
        Test to check that when creating a StoreItem, default
        values are assigned as follows: is_coins: False
        """
        new_store_item = StoreItem(name="Test Defaults", description="Blank", price=12.99, delivery_required=False)
        new_store_item.save()
        retrieved_new_item = StoreItem.objects.get(name="Test Defaults")
        self.assertFalse(retrieved_new_item.is_coins)

    def test_creating_store_item_requires_name_price_and_delivery_required(self):
        """
        Test to check that a name, price, and delivery_required value need to
        be provided when creating a StoreItem
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                without_name = StoreItem(price=99.99, delivery_required=True)
                without_name.save()

            with transaction.atomic():
                without_price = StoreItem(name="A Name", delivery_required=False)
                without_price.save()

            with transaction.atomic():
                without_delivery = StoreItem(name="Another Name", price=10.50)
                without_delivery.save()

    def test_creating_coins_purchase_requires_name_and_coins_price(self):
        """
        Test to check that a name and coins price are required to create
        a CoinsPurchase object
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                without_name = CoinsPurchase(coins_price=500)
                without_name.save()

            with transaction.atomic():
                without_price = CoinsPurchase(name="A Name")
                without_price.save()

    def test_creating_order_requires_a_user_value_only(self):
        """
        Test to check that creating an Order object only requires
        a value for user. delivery_address is optional. date_time should
        be set to current datetime
        """
        new_user = User.objects.create(username="Order test user", email="otu@email.com", password="something secret")
        only_user_order = Order(user=new_user)
        only_user_order.save()
        retrieved_order = Order.objects.get(user=new_user)
        self.assertEqual(retrieved_order.date_time.date(), datetime.date.today())

        with self.assertRaises(IntegrityError):
            order_without_user = Order()
            order_without_user.save()

    def test_all_fields_required_to_create_order_item(self):
        """
        Test to check that all fields are mandatory when creating an
        OrderItem. These fields are: order, item, quantity, total_purchase_price
        """
        random_order = choice(Order.objects.all())
        random_item = choice(StoreItem.objects.all())
        random_quantity_from_1_to_10 = choice(range(1, 11))
        total_purchase_price = (random_item.price * random_quantity_from_1_to_10)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                without_order = OrderItem(item=random_item, quantity=random_quantity_from_1_to_10,
                                          total_purchase_price=total_purchase_price)
                without_order.save()

            with transaction.atomic():
                without_item = OrderItem(order=random_order, quantity=random_quantity_from_1_to_10,
                                         total_purchase_price=total_purchase_price)
                without_item.save()

            with transaction.atomic():
                without_quantity = OrderItem(order=random_order, item=random_item,
                                             total_purchase_price=total_purchase_price)
                without_quantity.save()

            with transaction.atomic():
                without_total_price = OrderItem(order=random_order, item=random_item,
                                                quantity=random_quantity_from_1_to_10)
                without_total_price.save()

    def test_creating_user_coins_requires_user_value_only(self):
        """
        Test to check that creating a UserCoins requires  a value
        for user and nothing more
        """
        random_user = choice(User.objects.all())
        UserCoins.objects.create(user=random_user)

        with self.assertRaises(IntegrityError):
            UserCoins.objects.create()

    def test_user_coins_change_and_transaction_required_to_create_user_coins_history(self):
        """
        Test to check that a value for user, coins_change, and transaction are required
        in order to create a UserCoinHistory object. A UserCoinHistory objects
        should be able to be created with these values only
        """
        random_user = choice(User.objects.all())
        coins_change = choice([100, 223, 1000, -50, -900, 2])
        random_transaction = choice(range(1, 10))
        with_all_3 = UserCoinHistory(user=random_user, coins_change=coins_change, transaction=random_transaction)
        with_all_3.save()

        self.assertEqual(with_all_3.date_time.date(), datetime.date.today())

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                without_user = UserCoinHistory(coins_change=coins_change, transaction=random_transaction)
                without_user.save()

            with transaction.atomic():
                without_coins_change = UserCoinHistory(user=random_user, transaction=random_transaction)
                without_coins_change.save()

            with transaction.atomic():
                without_transaction = UserCoinHistory(user=random_user, coins_change=coins_change)
                without_transaction.save()
