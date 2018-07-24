from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User


class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserLoginForm(AuthenticationForm):
    pass
