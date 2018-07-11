from django.contrib import admin
from .models import Suggestion, Upvote, Comment
# Register your models here.

admin.site.register(Suggestion)
admin.site.register(Upvote)
admin.site.register(Comment)