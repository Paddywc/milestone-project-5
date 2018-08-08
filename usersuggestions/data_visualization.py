import datetime
from io import BytesIO
from random import choice

import boto3
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from django.conf import settings
from django.db.models import Count
from django.db.models import Q
from matplotlib.ticker import MultipleLocator, FuncFormatter
from mpld3 import fig_to_html

from market.models import UserCoinHistory
from .models import Suggestion, SuggestionAdminPage

plt.style.use('fivethirtyeight')


def get_highest_vote_totals(limit):
    """
    Returns the upvote totals for the feature suggestions with the
    most upvotes. The number of features returned is determined by the argument
    """
    return Suggestion.objects.filter(is_feature=True, suggestionadminpage__in_current_voting_cycle=True).annotate(
        upvotes=Count("upvote")).annotate(comments=Count("comment")).order_by("-upvotes")[:limit]


def get_coin_expenditures():
    """
    Returns the total coins SPENT on submitting, upvoting
    and promoting feature suggestions. Other coins transactions excluded
    as they add, rather than remove, coins from the user
    """
    expenditures = UserCoinHistory.objects.filter(Q(transaction=1) | Q(transaction=2) | Q(transaction=9))
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

    return {"submissions": spent_on_submissions, "upvoting": spent_on_upvoting,
            "promoting_suggestion": spent_on_promoting_suggestion}


def populate_completion_dates_chart():
    """
    Creates data to use in the features and bug completed in
    June chart. For each suggestion titled 'For populating chart',
    its compilation date is set as a random date in June 2018
    """
    start_date = datetime.date(2018, 6, 1)
    days_in_june = 30
    date_range = [start_date + datetime.timedelta(days=day) for day in range(0, (days_in_june + 1))]

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
    Returns all bugs and features titled "For populating chart". Returned
    as a dictionary, with values separated into bugs and features
    """
    bugs = SuggestionAdminPage.objects.filter(suggestion__title="For populating chart", suggestion__is_feature=False)

    features = SuggestionAdminPage.objects.filter(suggestion__title="For populating chart", suggestion__is_feature=True)

    return {"bugs": bugs, "features": features}


def create_most_upvoted_chart(limit):
    """
    Creates a bar chart for the most upvoted feature
    suggestions. Returns this chart as HTML
    """
    colors = "rgbymc"
    top_voted = get_highest_vote_totals(limit)
    x = [suggestion.title for suggestion in top_voted]

    y = [suggestion.upvotes for suggestion in top_voted]

    fig = plt.figure()

    plt.bar(x, y, color=colors)

    handles_list = []
    for i in range(len(x)):
        bar = mpatches.Patch(color=colors[i], label=x[i])
        handles_list.append(bar)

    plt.legend(handles=handles_list, shadow=True, title="SUGGESTION TITLE")
    plt.title("Most Upvoted Feature Suggestions")
    plt.ylabel("VOTES")
    plt.xlabel("SUGGESTION")

    plt.xticks([])
    chart = fig_to_html(fig)
    plt.close(fig)
    return chart


def create_coin_spending_chart():
    """
    Creates a pie chart for the percent of all coins spent
    on upvoting, promoting, and submitting feature suggestions. Returns
    this chart as HTML
    """
    totals = get_coin_expenditures()
    slices = [totals["upvoting"], totals["promoting_suggestion"], totals["submissions"]]
    labels = ["Upvoting Suggestions", "Promoting Suggestions", "Submitting Suggestions"]

    fig = plt.figure()
    plt.pie(slices, labels=None, autopct='%1.1f%%', startangle=90)
    plt.title("How Coins are Spent")
    plt.legend(labels=labels)

    chart = fig_to_html(fig)
    plt.close(fig)
    return chart


def get_data_for_june_completions_chart():
    """
    Returns a dictionary with the lists of the amount of bugs
    and features completed each day in June 2018. Includes null values
    """
    admin_suggestion_data = return_data_for_completion_dates_chart()

    june_days = [day for day in range(1, 31)]

    bugs = admin_suggestion_data["bugs"]
    features = admin_suggestion_data["features"]

    bug_completion_days = [bug.date_completed.day for bug in bugs]
    feature_completion_days = [feature.date_completed.day for feature in features]

    bug_june_day_counts = []
    feature_june_day_counts = []

    for june_day in june_days:
        bug_count = 0
        feature_count = 0
        for bug_day in bug_completion_days:
            if bug_day == june_day:
                bug_count += 1
        for feature_day in feature_completion_days:
            if feature_day == june_day:
                feature_count += 1

        bug_june_day_counts.append(bug_count)
        feature_june_day_counts.append(feature_count)

    return {"bug_june_day_counts": bug_june_day_counts, "feature_june_day_counts": feature_june_day_counts}


def create_completions_in_june_chart():
    """
    Creates a bar chart with counts of bugs and features completed each day in
    June 2018. Saved as img because mpld3 can't render tick marks properly, and unlike
    other charts, data are static. Img saved directly to S3 bucket
    """
    data = get_data_for_june_completions_chart()

    bug_june_day_counts = data["bug_june_day_counts"]
    feature_june_day_counts = data["feature_june_day_counts"]
    june_days = [day for day in range(0, 31)]

    def format_ticks_as_dates(x, i):
        if i == 1:
            return "1st"
        elif i != 0:
            return "{}th".format(int(x))
        else:
            return ""

    y_axis_height = [(bug_june_day_counts[day] + feature_june_day_counts[day]) for day in range(len(june_days))]
    max_y_axis_height = max(y_axis_height)

    minorLocator = MultipleLocator(1)
    majorFormatter = FuncFormatter(format_ticks_as_dates)
    majorLocator = MultipleLocator(5)

    fig, ax = plt.subplots()

    p1 = plt.bar(june_days, bug_june_day_counts)
    p2 = plt.bar(june_days, feature_june_day_counts, bottom=bug_june_day_counts)

    plt.yticks(range((max_y_axis_height + 1)))

    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_major_formatter(majorFormatter)
    ax.xaxis.set_minor_locator(minorLocator)

    # following 4 lines of code from:https://matplotlib.org/gallery/ticks_and_spines/major_minor_demo.html#sphx-glr-gallery-ticks-and-spines-major-minor-demo-py
    ax.tick_params(which='both', width=2)
    ax.tick_params(which='major', length=7)
    ax.tick_params(which='minor', length=4)
    plt.tight_layout()

    plt.ylabel("NUMBER COMPLETED")
    plt.xlabel("DATE")
    plt.title("Bug Fixes and Features Completed\nJune 2018")
    plt.legend(labels=["Bug Fixes", "Features"])

    # save img to aws
    # code largely from: https://stackoverflow.com/questions/31485660/python-uploading-a-plot-from-memory-to-s3-using-matplotlib-and-boto
    img_data = BytesIO()
    plt.savefig(img_data, format='png', bbox_inches='tight')
    img_data.seek(0)
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    bucket.put_object(Body=img_data, ContentType='image/png',
                      Key="{}/images/june_completions_chart.png".format(settings.MEDIAFILES_LOCATION))
    plt.close(fig)
