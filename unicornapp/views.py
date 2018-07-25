from django.shortcuts import render, redirect, get_object_or_404


# Create your views here.
def render_home(request):
    """
    """
    return render(request, "home.html")