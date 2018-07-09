from .models import UserCoins, CoinsPurchase

def add_coins(user, amount):
    """
    adds the amount specfied in the second
    argument to the argument user
    """
    print(amount)
    # below line of code creates table row for user if none exists
    UserCoins.objects.get_or_create(user=user)
    user_row = UserCoins.objects.get(user=user)
    old_coins_value = user_row.coins
    user_row.coins = old_coins_value + amount
    user_row.save()
    
def remove_coins(user, amount):
    """
    adds the amount specfied in the second
    argument to the argument user
    """
    UserCoins.objects.get_or_create(user=user)
    user_row = UserCoins.objects.get(user=user)
    old_coins_value = user_row.coins
    user_row.coins = old_coins_value - amount
    user_row.save()
    
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
    