from .models import Upvote

def add_upvote_to_database(user, suggestion):
    """
    """
    upvote = Upvote(user=user, suggestion=suggestion)
    upvote.save()