from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def create_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {"form": form})