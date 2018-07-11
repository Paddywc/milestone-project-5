from django.db import models
from accounts.models import User
from ckeditor_uploader.fields import RichTextUploadingField 

# Create your models here.
class Suggestion(models.Model):
    suggestion_choices = ((True, 'Feature'), (False, 'Bug Fix'))
    
    is_feature = models.BooleanField(blank=False, default=False, choices=suggestion_choices)
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    title = models.CharField(max_length=200, blank=False)
    details = RichTextUploadingField()
    date_time = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return "{0}: {1}".format(self.user, self.title)
    

class SuggestionAdminPage(models.Model):
    
    status_choices = ((0,"not scheduled"), (1,"to do"), (2,"doing"), (3, "done"))
    priority_choices = ((0,"low"),(1,'normal'),(2,'high'))
    
    suggestion = models.ForeignKey(Suggestion, null=False, on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(choices=status_choices, default=0)
    developer_assigned = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    priority = models.PositiveSmallIntegerField(choices=priority_choices, null=True, blank=True, default=1)
    date_time_started = models.DateTimeField(null=True, blank=True)
    expected_completion_date_time = models.DateTimeField(null=True, blank=True)
    github_branch = models.CharField(null=True, blank=True, max_length=50)
    
    def __str__(self):
        return self.suggestion.title
        
            

class Comment(models.Model):
    """
    """
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    suggestion = models.ForeignKey(Suggestion, null=False, on_delete=models.CASCADE)
    admin_page_comment= models.BooleanField(blank=False, default=False)
    comment = RichTextUploadingField()
    date_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{0}: {1}".format(self.user, self.suggestion.title)
        
class Upvote(models.Model):
    """
    """
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    suggestion = models.ForeignKey(Suggestion, null=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, null=True, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        try:
            return "{0}:Suggestion:{1}".format(self.user,self.suggestion.title)
        except:
            return "{0}: Comment on Suggestion: {1}".format(self.user,self.comment.suggestion.title)
            
