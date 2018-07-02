# Code from: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#auth-custom-user
# For creating a custom user class
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.register(User, UserAdmin)
