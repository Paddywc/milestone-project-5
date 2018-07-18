import matplotlib.pyplot as plt
from .models import Suggestion
from django.db.models import Count

def get_highest_vote_totals(limit):
    """
    """
    return Suggestion.objects.filter(is_feature=True, suggestionadminpage__in_current_voting_cycle=True).annotate(upvotes=Count("upvote")).annotate(comments=Count("comment")).order_by("-upvotes")[:limit]
    
