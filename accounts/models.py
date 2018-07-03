from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    # from https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
    # makes emailed required and have to be unique
    # USERNAME_FIELD = "email"
    email = models.EmailField(('email address'), blank=False, unique=True)
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.username