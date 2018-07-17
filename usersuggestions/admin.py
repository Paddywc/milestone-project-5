from django.contrib import admin
from .models import Suggestion, Upvote, Comment, SuggestionAdminPage, Flag, PromotedFeatureSuggestion
# Register your models here.

admin.site.register(Suggestion)
admin.site.register(SuggestionAdminPage)
admin.site.register(Upvote)
admin.site.register(Comment)
admin.site.register(Flag)
admin.site.register(PromotedFeatureSuggestion)