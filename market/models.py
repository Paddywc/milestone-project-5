from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from accounts.models import User

# below class taken from ecommerce project
class StoreItem(models.Model):
    name = models.CharField(max_length=200, default="")
    description= models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='images')
    
    def __str__(self):
        return self.name
        
        

        
class Delivery(models.Model):
    """
    Delivery details
    """
    
    
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=50, blank=False)
    # phone_number = PhoneNumberField()
    phone_number = models.CharField(max_length=20, blank=False)
    street_address1 = models.CharField(max_length=40, blank=False)
    street_address2 = models.CharField(max_length=40, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    town_or_city = models.CharField(max_length=40, blank=False)
    county = models.CharField(max_length=50, blank=False)
    country = CountryField()

    def __str__(self):
        return "{0}:{1},{2},{3}".format(self.user, self.full_name, self.street_address1, self.postcode)
    
    
class Order(models.Model):
    """
    """
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    def __str__(self):
        return "{0}-{1}-{2}".format(self.user, self.date.date(), self.full_name)
        
class OrderItem(models.Model):
    """
    """
    order = models.ForeignKey(Order, null=False, on_delete=models.CASCADE)
    item = models.ForeignKey(StoreItem, null=False, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False)

    def __str__(self):
        return "{0}-{1}-{2}".format(self.quantity, self.item.name, self.item.price)
        
