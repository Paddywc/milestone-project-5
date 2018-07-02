from django.shortcuts import render
from django.contrib.auth import login
from .forms import UserSignupForm, UserLoginForm

# Create your views here.

def create_user(request):
    """
    Creates a new (non-admin) user and stores
    them in the database
    """
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = UserSignupForm()
        
    return render(request, 'signup.html', {"form": form})
    
def login_user(request):
    """
    Code from
    https://www.youtube.com/watch?v=XMgF3JwKzgs&list=PL4cUxeGkcC9ib4HsrXEYpQnTOTZE1x0uc&index=22
    Above video showed form.get_user and login
    """
    if request.method=="POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
    else:
        form = UserLoginForm()
        
    return render(request, 'login.html', {"form": form})