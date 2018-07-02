from .models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserSignupForm(UserCreationForm):
    
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        
class UserLoginForm(AuthenticationForm):
    
   pass