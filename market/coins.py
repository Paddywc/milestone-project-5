from .models import UserCoins

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
    
