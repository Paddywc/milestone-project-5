from .models import Upvote

def add_suggestion_upvote_to_database(user, suggestion):
    """
    """
    upvote = Upvote(user=user, suggestion=suggestion)
    upvote.save()
    
def add_comment_upvote_to_database(user, comment):
    upvote = Upvote(user=user, comment=comment)
    upvote.save()