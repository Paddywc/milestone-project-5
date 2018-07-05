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
    delivery_required = models.BooleanField(blank=False)
    
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
    current_delivery_method = models.BooleanField(default=True)
    def __str__(self):
        return "{0}:{1},{2},{3}".format(self.user, self.full_name, self.street_address1, self.postcode)
    
    # Code for turning other current_delivery_method values
    # to False once a new value saved as a True
    # Code from: https://stackoverflow.com/questions/1455126/unique-booleanfield-value-in-django
    def save(self, *args, **kwargs):
        if self.current_delivery_method:
            try:
                temp = Delivery.objects.get(current_delivery_method=True)
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
    date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.ForeignKey(Delivery, null=True, on_delete=models.PROTECT)
    def __str__(self):
        return "{0}-{1}".format(self.user, self.date.date())
        
class OrderItem(models.Model):
    """
    """
    order = models.ForeignKey(Order, null=False, on_delete=models.CASCADE)
    item = models.ForeignKey(StoreItem, null=False, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False)

    def __str__(self):
        return "{0}-{1}-{2}".format(self.quantity, self.item.name, self.item.price)
        
