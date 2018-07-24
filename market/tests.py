from django.test import TestCase
from .models import CoinsPurchase, StoreItem, UserCoinHistory, Order, OrderItem, UserCoins
from random import choice
from accounts.models import User
from usersuggestions.models import Suggestion
from .coins import add_transaction_to_user_coin_history, return_minimum_coins_purchase, add_coins,remove_coins, return_user_coins, get_coins_price, return_all_store_coin_options
class TestCoins(TestCase):
    
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
        coins_store_item_200 = StoreItem(name="200 coins", price=0, delivery_required=False, is_coins=True,
                                         coins_amount=200)
        coins_store_item_200.save()
        coins_store_item_1000 = StoreItem(name="1000 coins", price=0, delivery_required=False, is_coins=True,
                                         coins_amount=1000)
        coins_store_item_1000.save()
        
        non_coins_store_item = StoreItem(name="not coins", price=5, delivery_required=True, is_coins=False)
        non_coins_store_item.save()
        
    def test_can_add_to_usercoin_history(self):
        """
        Test to check that add_transaction_to_user_coin_history creates
        a UserCoinHistory object from its arguments. Object should include 
        a suggestion if one if provided in the function's arguments
        """
        user = User.objects.get(id=1)
        add_transaction_to_user_coin_history(user, 200, 1)
        returned_transaction = UserCoinHistory.objects.get(user=user)
        self.assertEqual(returned_transaction.transaction,1)
        self.assertEqual(returned_transaction.coins_change, 200)
        
        user_2 = User.objects.get(id=2)
        random_suggestion = choice(Suggestion.objects.all())
        add_transaction_to_user_coin_history(user_2, -100, 3, random_suggestion)
        returned_transaction_2 = UserCoinHistory.objects.get(user=user_2)
        self.assertEqual(returned_transaction_2.transaction, 3)
        self.assertEqual(returned_transaction_2.coins_change, -100)
        self.assertEqual(returned_transaction_2.suggestion, random_suggestion)
        
        
    def test_can_add_and_remove_coins(self):
        """
        Test to check that add_coins adds coins to the argument user's 
        UserCoins row, and remove_coins removes them
        """
        user_1 = choice(User.objects.all())
        previous_coins = UserCoins.objects.get(user=user_1).coins
        add_coins(user_1, 100, 2)
        coins_after_addition = UserCoins.objects.get(user=user_1).coins
        self.assertEqual((coins_after_addition-100), previous_coins)
        
        remove_coins(user_1, 300, 4)
        coins_after_subtraction  = UserCoins.objects.get(user=user_1).coins
        self.assertEqual((coins_after_subtraction+300),coins_after_addition)
        
        
    def test_queries_create_row_for_user_if_none_exits(self):
        """
        Test to check that add_coins, remove_coins, and return_user_coins 
        create a row in UserCoins for the user if none exists
        """
        
        new_user_1 = User(username="new user 1", email="nu1@email.com", password="password")
        new_user_1.save()
        self.assertEqual(len(UserCoins.objects.filter(user=new_user_1)), 0)
        add_coins(new_user_1, 100, 4)
        self.assertEqual(len(UserCoins.objects.filter(user=new_user_1)), 1)
        
        new_user_2 = User(username="new user 2", email="nu2@email.com", password="password")
        new_user_2.save()
        self.assertEqual(len(UserCoins.objects.filter(user=new_user_2)), 0)
        remove_coins(new_user_2, 200, 6)
        self.assertEqual(len(UserCoins.objects.filter(user=new_user_2)), 1)
        
        new_user_3 = User(username="new user 3", email="nu3@email.com", password="password")
        new_user_3.save()
        self.assertEqual(len(UserCoins.objects.filter(user=new_user_3)), 0)
        return_user_coins(new_user_3)
        self.assertEqual(len(UserCoins.objects.filter(user=new_user_3)), 1)
        
        
    def test_can_return_coins_price_for_coins_purchase(self):
        """
        Test to check that get_coins_price returns the price of 
        the CoinsPurchase named in the argument
        """
        random_coins_price = choice(range(1, 1000))
        new_coins_purchase = CoinsPurchase(name="Test Purchase", coins_price=random_coins_price)
        new_coins_purchase.save()
        
        price = get_coins_price("Test Purchase")
        self.assertEqual(price, random_coins_price)
        
    
    def test_store_coin_options_ordered_by_coins_amount(self):
        """
        Test to check that the results of return_all_store_coin_options
        are sorted from least coins to most coins
        """
        
        coin_options = return_all_store_coin_options()
        previous_entry_coins_amount = 0
        for option in coin_options:
            self.assertTrue(option.is_coins)
            self.assertTrue(option.coins_amount >= previous_entry_coins_amount)
            previous_entry_coins_amount = option.coins_amount
            
            
    def test_that_return_minimum_coins_returns_the_smallest_amount_of_coins_required_to_meet_item_cost(self):
        """
        Test that the StoreItem returned by return_minimum_coins_purchase is coins, 
        and when summed with the second argument it should be >= the first argument. It should 
        be the StoreItem with the smallest amount of coins that meets this criteria
        """
        
        coin_options = return_all_store_coin_options()
        
        random_item_cost_under_1000 = choice(range(1, 1000))
        minimum_purchase = return_minimum_coins_purchase(random_item_cost_under_1000, 0)
        self.assertTrue(minimum_purchase.coins_amount >= random_item_cost_under_1000)
        
        possible_options = [option.coins_amount for option in coin_options if option.coins_amount >= random_item_cost_under_1000]
        self.assertEqual(min(possible_options), minimum_purchase.coins_amount)
            
        minimum_purchase_2 = return_minimum_coins_purchase(random_item_cost_under_1000, 300)
        self.assertTrue(minimum_purchase.coins_amount >= (random_item_cost_under_1000-300))
        
        possible_options_2 = [option.coins_amount for option in coin_options if (option.coins_amount + 300) >= random_item_cost_under_1000]
        self.assertEqual(min(possible_options_2), minimum_purchase_2.coins_amount)
        