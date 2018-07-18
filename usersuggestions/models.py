from django.db import models
from accounts.models import User
from ckeditor_uploader.fields import RichTextUploadingField 
import datetime

# Create your models here.
class Suggestion(models.Model):
    suggestion_choices = ((True, 'Feature'), (False, 'Bug Fix'))
    
    is_feature = models.BooleanField(blank=False, default=False, choices=suggestion_choices)
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    title = models.CharField(max_length=200, blank=False)
    details = RichTextUploadingField()
    date_time = models.DateTimeField(auto_now_add=True)
    delay_submission = models.BooleanField(null=False, blank=True, default=False)
    
    def __str__(self):
        return "{0}: {1}".format(self.user, self.title)
    

class SuggestionAdminPage(models.Model):
    
    status_choices = ((0,"not scheduled"), (1,"to do"), (2,"doing"), (3, "done"))
    priority_choices = ((0,"low"),(1,'normal'),(2,'high'))
    
    suggestion = models.ForeignKey(Suggestion, null=False, on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(choices=status_choices, default=0)
    developer_assigned = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    priority = models.PositiveSmallIntegerField(choices=priority_choices, null=True, blank=True, default=1)
    date_started = models.DateField(null=True, blank=True)
    estimated_days_to_complete =  models.PositiveSmallIntegerField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    date_completed = models.DateField(null=True, blank=True)
    github_branch = models.CharField(null=True, blank=True, max_length=50)
    in_current_voting_cycle = models.BooleanField(blank=False, default=True)
    was_successful = models.NullBooleanField(blank=True, null=True) 
    current_winner = models.BooleanField(blank=False, default=False)
    
    def __str__(self):
        return self.suggestion.title
        
            
    # Code for turning other current_winner values
    # to False once a new value saved as a True
    # Code from: https://stackoverflow.com/questions/1455126/unique-booleanfield-value-in-django
    def save(self, *args, **kwargs):
        if self.current_winner:
            try:
                temp = SuggestionAdminPage.objects.get(current_winner=True)
                if self != temp:
                    temp.current_winner = False
                    temp.save()
            except SuggestionAdminPage.DoesNotExist:
                pass
        super(SuggestionAdminPage, self).save(*args, **kwargs)
        
        # My code
        # For setting completed date automatically once status set to done
        if self.status==3:
            try:
                self.date_completed = datetime.date.today()
            
            except SuggestionAdminPage.DoesNotExist:
                pass
        super(SuggestionAdminPage, self).save(*args, **kwargs)

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
            
class Flag(models.Model):
    """
    """
    
    flagged_item_choices  = ((1,"comment"),(2,'suggestion'))
    result_choices = ((0,"low"),(1,'normal'),(2,'high'))
    status_choices = ((0,"not scheduled"), (1,"to do"), (2,"doing"), (3, "done"))
    reason_choices = ((0,"Spam"), (1,"Hate Speech"), (2,"Graphic Content"), (3, "Harassment or Bullying"))
    
    flagged_item_type = models.PositiveSmallIntegerField(choices=flagged_item_choices, null=False)
    flagged_by = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    suggestion = models.ForeignKey(Suggestion, null=True, on_delete=models.SET_NULL)
    comment =  models.ForeignKey(Comment, null=True, on_delete=models.SET_NULL)
    reason = models.PositiveSmallIntegerField(choices=reason_choices)
    date_time_marked = models.DateTimeField(auto_now_add=True)
    admin_assigned = models.ForeignKey(User, related_name="admin_assigned", null=True, blank=True, on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(choices=status_choices, default=0)
    deemed_inappropriate = models.NullBooleanField(blank=True, null=True) 
    
    def __str__(self):
        return "Flagged {0}. {1}. {2}".format(self.get_flagged_item_type_display(), self.date_time_marked, self.get_status_display())
        
        
class UserFavorites(models.Model):
    """
    """
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    suggestion = models.ForeignKey(Suggestion, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return "{0}: {1}".format(self.user, self.suggestion)
        
class PromotedFeatureSuggestion(models.Model):
    """
    """
    user = models.ForeignKey(User, null=False, on_delete=models.PROTECT)
    suggestion = models.ForeignKey(Suggestion, null=True, on_delete=models.CASCADE)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=False, null=False)
    
    def __str__(self):
        return "{0}: {1}-{2}".format(self.suggestion, self.start_date, self.end_date)
        
    