from .models import UserCoins, CoinsPurchase, StoreItem, UserCoinHistory
from usersuggestions.models import Suggestion, Comment

def add_transaction_to_user_coin_history(user, amount, purchase=False, transaction=0):
    """
    """
    user_coins_row = UserCoins.objects.get(user=user)
    if purchase:
        if isinstance(purchase, Suggestion):
            transaction = UserCoinHistory(user=user,coins_change=amount, suggestion=purchase, transaction=transaction)
        else:
            transaction = UserCoinHistory(user=user, coins_change=amount, transaction=transaction)
    else:
        transaction = UserCoinHistory(user=user,coins_change=amount)
    transaction.save()
    


def add_coins(user, amount, transaction=0):
    """
    adds the amount specfied in the second
    argument to the argument user. Adds transaction
    to UserCoinHistory
    """
    # below line of code creates table row for user if none exists
    UserCoins.objects.get_or_create(user=user)
    user_row = UserCoins.objects.get(user=user)
    old_coins_value = user_row.coins
    user_row.coins = old_coins_value + amount
    user_row.save()
    add_transaction_to_user_coin_history(user, amount, True, transaction)
    
def remove_coins(user, amount, purchase=False, transaction=0):
    """
    adds the amount specfied in the second
    argument to the argument user. Adds transaction
    to UserCoinHistory
    """
    UserCoins.objects.get_or_create(user=user)
    user_row = UserCoins.objects.get(user=user)
    old_coins_value = user_row.coins
    user_row.coins = old_coins_value - amount
    user_row.save()
    
    if purchase:
        add_transaction_to_user_coin_history(user,(0-amount), purchase, transaction)
    else:
        add_transaction_to_user_coin_history(user, (0-amount))
    
def return_user_coins(user):
    """
    Returns the amount of coins that
    the argument user has
    """
    UserCoins.objects.get_or_create(user=user)
    user_row = UserCoins.objects.get(user=user)
    return user_row.coins
    

def get_coins_price(name):
    """
    Returns the argument's price in coins
    """
    return CoinsPurchase.objects.get(name=name).coins_price
    
def return_all_store_coin_options():
    """
    Returns all the coin variations available
    as store items. Sorted in accessing order
    """
    return StoreItem.objects.filter(is_coins=True).order_by("coins_amount")
    
def return_minimum_coins_purchase(item_cost, user_coins):
    """
    Returns the minimum purchase of coins required
    for the argument user to be able to purchase the
    argument item
    """
    coin_options = return_all_store_coin_options()
    for coin_option in coin_options:
        if (coin_option.coins_amount + user_coins) >= item_cost:
            return coin_option
    
