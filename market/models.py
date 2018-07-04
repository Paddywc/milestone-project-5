from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

# below class taken from ecommerce project
class StoreItem(models.Model):
    name = models.CharField(max_length=200, default="")
    description= models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='images')
    
    def __str__(self):
        return self.name
        
        
class Order(models.Model):
    """
    """
    full_name = models.CharField(max_length=50, blank=False)
    phone_number = PhoneNumberField()
    street_address1 = models.CharField(max_length=40, blank=False)
    street_address2 = models.CharField(max_length=40, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    town_or_city = models.CharField(max_length=40, blank=False)
    county = models.CharField(max_length=50, blank=False)
    country = CountryField()
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{0}-{1}-{2}".format(self.id, self.date, self.full_name)
        
class OrderItem(models.Model):
    """
    """
    order = models.ForeignKey(Order, null=False, on_delete=models.CASCADE)
    item = models.ForeignKey(StoreItem, null=False, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False)

    def __str__(self):
        return "{0}-{1}-{2}".format(self.quantity, self.item.name, self.item.price)