import matplotlib.pyplot as plt
from .models import Suggestion, SuggestionAdminPage
from market.models import UserCoinHistory
from django.db.models import Count
from django.db.models import Q
import datetime
from random import choice
import matplotlib.patches as mpatches
from mpld3 import fig_to_html

def get_highest_vote_totals(limit):
    """
    """
    return Suggestion.objects.filter(is_feature=True, suggestionadminpage__in_current_voting_cycle=True).annotate(upvotes=Count("upvote")).annotate(comments=Count("comment")).order_by("-upvotes")[:limit]
    
def get_coin_expenditures(): 
    """
    Spending only
    """
    expenditures = UserCoinHistory.objects.filter(Q(transaction=1)| Q(transaction=2)|Q(transaction=9))
    spent_on_submissions = 0
    spent_on_upvoting = 0
    spent_on_promoting_suggestion = 0
    
    for row in expenditures:
        if row.transaction == 1:
            spent_on_submissions -= row.coins_change
        elif row.transaction == 2:
            spent_on_upvoting -= row.coins_change
        else:
            spent_on_promoting_suggestion -= row.coins_change
    
    return{"submissions": spent_on_submissions, "upvoting": spent_on_upvoting, "promoting_suggestion": spent_on_promoting_suggestion}
    
def populate_completion_dates_chart():
    """
    Dates in June
    Code partly from ://stackoverflow.com/questions/993358/creating-a-range-of-dates-in-python
    """
    start_date = datetime.date(2018, 6,1)
    # end_date = datetime.date(2018, 6, 30)
    days_in_june = 30
    date_range = [start_date + datetime.timedelta(days=day) for day in range(0, (days_in_june+1))]
    
        
    def get_random_date():
        random_date = choice(date_range)
        return random_date
        
    
    population_rows = SuggestionAdminPage.objects.filter(suggestion__title="For populating chart")
    
    for row in population_rows:
        row.status = 3
        row.date_completed = get_random_date()
        row.in_current_voting_cycle = False
        row.save()
        

def return_data_for_completion_dates_chart():
    """
    """
    bugs = SuggestionAdminPage.objects.filter(suggestion__title="For populating chart", suggestion__is_feature=False)
    
    features = SuggestionAdminPage.objects.filter(suggestion__title="For populating chart", suggestion__is_feature=True)
    
    
    return {"bugs": bugs, "features": features}
    
def create_most_upvoted_chart(limit):

    colors = "rgbymc"
    top_voted = get_highest_vote_totals(limit)
    x = [suggestion.title for suggestion in top_voted]
    
    y = [suggestion.upvotes for suggestion in top_voted]
    
    blank_x = ["", " ", "  ", "   ", "    ",]
    blank_x_2 = [((" ") * i) for i in range(1, (limit+1))]
    print(blank_x)
    
    
    fig = plt.figure()
    plt.style.use('fivethirtyeight')

    plt.bar(blank_x,y, color=colors)
    

    handles_list = []
    for i in range(len(x)):
        bar = mpatches.Patch(color=colors[i], label=x[i])
        handles_list.append(bar)
        
        
    plt.legend(handles=handles_list, shadow=True, title="SUGGESTION TITLE")
    plt.title("Most Upvoted Feature Suggestions")
    plt.ylabel("VOTES")
    plt.xlabel("SUGGESTION")
    
    plt.xticks([])
    # fig.axis.get_xaxis().set_visable(False)
    chart = fig_to_html(fig)
    
    return chart

    
    
    
    