from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # from https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username
    # Sets it so that user logs in user their email
    USERNAME_FIELD = "email"
    email = models.EmailField('email address', blank=False, unique=True)
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
