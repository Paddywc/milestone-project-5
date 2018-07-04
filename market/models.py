from django.db import models

# below class taken from ecommerce project
class StoreItem(models.Model):
    name = models.CharField(max_length=200, default="")
    description= models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='images')
    
    def __str__(self):
        return self.name
        