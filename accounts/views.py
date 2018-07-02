from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def create_user(request):
    form = UserCreationForm()
    return render(request, 'signup.html', {"form": form})