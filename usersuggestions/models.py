from django.db import models
from accounts.models import User

# Create your models here.
class Suggestion(models.Model):
    feature = models.BooleanField(blank=False, default=False)
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    title = models.CharField(max_length=200, blank=False)
    details = models.CharField(max_length=200, blank=False)
    date_time = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return "{0}: {1}".format(self.user, self.title)
    
    