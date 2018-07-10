from django.contrib import admin
from .models import Suggestion, Upvote
# Register your models here.

admin.site.register(Suggestion)
admin.site.register(Upvote)