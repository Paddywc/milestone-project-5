from django.db import models
from django_countries.fields import CountryField

from accounts.models import User
from usersuggestions.models import Suggestion


# below class taken from ecommerce project
class StoreItem(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='images')
    delivery_required = models.BooleanField(blank=False, null=False)
    is_coins = models.BooleanField(default=False, null=False)
    coins_amount = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class CoinsPurchase(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(blank=True)
    coins_price = models.PositiveIntegerField(blank=False)

    def __str__(self):
        return self.name


class Delivery(models.Model):
    """
    Delivery details
    """

    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=50, blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    street_address_1 = models.CharField(max_length=40, blank=False)
    street_address_2 = models.CharField(max_length=40, blank=True)
    postcode = models.CharField(max_length=20, blank=False, null=False)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    county = models.CharField(max_length=50, blank=False, null=False)
    country = CountryField(blank=False, null=False)
    current_delivery_method = models.BooleanField(default=True)

    def __str__(self):
        return "{0}: {1}".format(self.user, self.postcode)

    # Code for turning other current_delivery_method values
    # to False once a new value saved as a True
    # Code from: https://stackoverflow.com/questions/1455126/unique-booleanfield-value-in-django
    # Added user=self.user
    def save(self, *args, **kwargs):
        if self.current_delivery_method:
            try:
                temp = Delivery.objects.get(current_delivery_method=True, user=self.user)
                if self != temp:
                    temp.current_delivery_method = False
                    temp.save()
            except Delivery.DoesNotExist:
                pass
        super(Delivery, self).save(*args, **kwargs)


class Order(models.Model):
    """
    """
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    date_time = models.DateTimeField(auto_now_add=True)
    delivery_address = models.ForeignKey(Delivery, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return "{0}: {1}".format(self.user, self.date_time.date())


class OrderItem(models.Model):
    """
    """
    order = models.ForeignKey(Order, null=False, on_delete=models.CASCADE)
    item = models.ForeignKey(StoreItem, null=False, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False)
    total_purchase_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return "{0}-{1}-{2}".format(self.quantity, self.item.name, self.item.price)


class UserCoins(models.Model):
    """
    """
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    coins = models.PositiveIntegerField(null=True, default=0)

    def __str__(self):
        return "{0}: {1}".format(self.user, self.coins)


class UserCoinHistory(models.Model):
    """
    """
    transaction_choices = ((1, 'submission'), (2, 'upvote'), (3, 'referral'),
                           (4, 'store purchase'), (5, 'initial signup'), (6, 'received referral'),
                           (7, 'suggestion upvoted'), (8, 'suggestion successful'), (9, 'feature suggestion promoted'))

    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    coins_change = models.IntegerField(null=False)
    date_time = models.DateTimeField(auto_now_add=True)
    suggestion = models.ForeignKey(Suggestion, null=True, blank=True, on_delete=models.CASCADE)
    transaction = models.PositiveSmallIntegerField(choices=transaction_choices, blank=False, null=False)

    def __str__(self):
        return "{0}: {1} : {2}".format(self.user, self.get_transaction_display(), self.coins_change)
