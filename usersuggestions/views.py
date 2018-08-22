import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

import market.coin_prices.coin_rewards as coin_rewards
from market.coins import return_user_coins, add_coins, get_coins_price, remove_coins, return_all_store_coin_options, \
    return_minimum_coins_purchase, purchase_coins_for_action, purchase_coins_for_feature_promotion
from market.helpers import get_promote_feature_discount_rates, get_feature_promotion_prices
from .data_visualization import create_most_upvoted_chart, create_coin_spending_chart
from .forms import SuggestionForm, CommentForm, SuggestionAdminPageForm
from .helpers import return_current_features, \
    return_all_current_bugs, \
    return_public_suggestion_comments, return_admin_suggestion_comments, update_suggestion_admin_page, \
    set_initial_session_form_title_as_false, \
    return_previous_suggestion_form_values_or_empty_form, set_session_form_values_as_false, \
    submit_feature_promotion, get_promoted_features
from .models import Suggestion, Comment, SuggestionAdminPage, Flag
from .voting import add_suggestion_upvote_to_database, add_comment_upvote_to_database, \
    get_voting_end_date, return_completed_suggestions, end_voting_cycle_if_current_end_date


@login_required()
def add_suggestion(request):
    """
    Renders add suggestion page. User can purchase more coins
    if they have insufficient coins to submit feature  suggestions.
    In these case, their current form values are saved and returned
    once they are redirected back from the store.
    """
    set_initial_session_form_title_as_false(request)

    form = return_previous_suggestion_form_values_or_empty_form(request)

    if request.method == "POST":

        # if the user has insufficient coins for suggestion 
        # and opts to purchase more
        if 'purchaseCoins' in request.POST:
            current_form = SuggestionForm(data=request.POST)
            request.session["form_title"] = current_form["title"].data
            request.session["form_details"] = current_form["details"].data
            return purchase_coins_for_action(request)

        else:
            form = SuggestionForm(data=request.POST)
            # below line of code returns true if is_feature ==
            # 'feature'. Returns False if == 'bug fix'. Returned as String
            is_feature = request.POST.get("is_feature")
            if form.is_valid():
                saved_suggestion_object = form.save()
                if is_feature == 'True' and settings.COINS_ENABLED:
                    remove_coins(request.user, get_coins_price("Suggestion"), 1)
                    user_coins = return_user_coins(request.user)

                if saved_suggestion_object.delay_submission:
                    suggestion_admin_page = SuggestionAdminPage(suggestion=saved_suggestion_object,
                                                                in_current_voting_cycle=False)
                    messages.success(request,
                                     "Suggestion successfully submitted. It will be posted as the end of the current voting cycle")
                else:
                    suggestion_admin_page = SuggestionAdminPage(suggestion=saved_suggestion_object)
                    messages.success(request, "Suggestion successfully submitted!")
                suggestion_admin_page.save()
                set_session_form_values_as_false(request)
                return redirect("view_suggestion", saved_suggestion_object.id)

    if settings.COINS_ENABLED:
        price = get_coins_price("Suggestion")
        user_coins = return_user_coins(request.user)
        minimum_coins = return_minimum_coins_purchase(price, user_coins)
        coin_options = return_all_store_coin_options()
        return render(request, 'add_suggestion.html',
                      {"form": form, "coins_enabled": settings.COINS_ENABLED, "user_coins": user_coins, "price": price,
                       "coin_options": coin_options, "minimum_coins": minimum_coins})
    else:
        return render(request, 'add_suggestion.html',
                      {"form": form, "coins_enabled": settings.COINS_ENABLED})


def render_issue_tracker(request, sorting="-upvotes"):
    """
    Renders main suggestions page. Users can sort results
    by upvotes and age
    """
    end_voting_cycle_if_current_end_date()
    voting_end_date = get_voting_end_date()
    current_features = return_current_features(sorting)
    bugs = return_all_current_bugs(sorting)
    completed_suggestions = return_completed_suggestions()
    current_winner = SuggestionAdminPage.objects.get(current_winner=True)
    promoted_features = get_promoted_features()
    return render(request, "issue_tracker.html", {"features": current_features, "bugs": bugs,
                                                  "voting_end_date": voting_end_date,
                                                  "promoted_features": promoted_features,
                                                  "completed_suggestions": completed_suggestions,
                                                  "current_winner": current_winner})


def view_suggestion(request, id, comment_sorting="oldest"):
    """
    Renders suggestion page. Users can upvote and post
    comments to suggestion. If users have insufficient coins
    to upvote a feature suggestion, they can be redirected to the store.
    The current url is saved as the session_url, and users are redirected to
    this url after purchasing coins. Users can sort comments  by age and upvotes
    """
    coins_enabled = settings.COINS_ENABLED
    suggestion = get_object_or_404(Suggestion, id=id)
    suggestion_admin = get_object_or_404(SuggestionAdminPage, suggestion=suggestion)
    comments = return_public_suggestion_comments(suggestion, comment_sorting)
    form = CommentForm(initial={"user": request.user, "suggestion": suggestion})

    if request.user.is_authenticated:
        check_comment_users = True
    else:
        check_comment_users = False

    if request.method == "POST":
        if 'purchaseCoins' in request.POST:
            return purchase_coins_for_action(request)

        elif 'postComment' in request.POST:
            if request.user.is_authenticated:
                form = CommentForm(data=request.POST)
                if form.is_valid():
                    form.save()
            else:
                return redirect("login")

    if coins_enabled and request.user.is_authenticated:
        price = get_coins_price("Upvote")
        user_coins = return_user_coins(request.user)
        minimum_coins = return_minimum_coins_purchase(price, user_coins)
        coin_options = return_all_store_coin_options()

    else:
        price = None
        user_coins = None
        minimum_coins = None
        coin_options = None

    if suggestion.is_feature:
        return render(request, "view_feature.html",
                      {"form": form, "comments": comments, "feature": suggestion, "coins_enabled": coins_enabled,
                       "price": price, "user_coins": user_coins, "minimum_coins": minimum_coins,
                       "coin_options": coin_options, "suggestion_admin": suggestion_admin,
                       "check_comment_users": check_comment_users})

    else:
        return render(request, "view_bug.html",
                      {"form": form, "comments": comments, "bug": suggestion, "coins_enabled": coins_enabled,
                       "suggestion_admin": suggestion_admin, "check_comment_users": check_comment_users})


@login_required
def render_suggestion_admin_page(request, id):
    """
    Renders admin page for a suggestion. If user does not have
    staff status, redirects them to the public suggestion page. Admin
    can change values of the SuggestionAdminPage object
    """
    if not request.user.is_staff:
        return redirect("view_suggestion", id=id)
    suggestion = get_object_or_404(Suggestion, id=id)
    admin_page_values = get_object_or_404(SuggestionAdminPage, suggestion=suggestion)
    if request.method == "POST":

        if "postComment" in request.POST:
            form = CommentForm(data=request.POST)
            if form.is_valid():
                form.save()

        elif "adminPageSubmit" in request.POST:
            form = SuggestionAdminPageForm(data=request.POST)
            if form.is_valid():
                update_suggestion_admin_page(form)

    form = SuggestionAdminPageForm(instance=admin_page_values)
    comment_form = CommentForm(initial={"user": request.user, "suggestion": suggestion, "admin_page_comment": True, })
    comments = return_admin_suggestion_comments(suggestion)

    return render(request, "suggestion_admin_page.html",
                  {"form": form, "comment_form": comment_form, "comments": comments, "suggestion": suggestion})


@login_required
def upvote_suggestion(request, id):
    """
    View for upvoting a suggestion. An upvote is only added if the
    user has not already upvoted that suggestion.  However, if coins are
    enabled, users can add several upvotes to the same FEATURE suggestion
    """
    suggestion = get_object_or_404(Suggestion, id=id)
    if settings.COINS_ENABLED and suggestion.is_feature:
        remove_coins(request.user, get_coins_price("Upvote"), 2)
        add_coins(suggestion.user, coin_rewards.suggestion_upvoted, 7)
    already_upvoted = add_suggestion_upvote_to_database(request.user, suggestion)
    if already_upvoted:
        messages.info(request, "You have already upvoted this suggestion")
    else:
        messages.info(request, "Suggestion upvoted")
    return redirect("view_suggestion", id)


@login_required
def upvote_comment(request, id):
    """
    View for upvoting a comment. Upvote only added if
    user has not already upvoted that comment
    """
    comment = get_object_or_404(Comment, id=id)
    already_upvoted = add_comment_upvote_to_database(request.user, comment)
    if already_upvoted:
        messages.info(request, "You have already upvoted this comment")
    else:
        messages.info(request, "Comment upvoted")
    return redirect("view_suggestion", comment.suggestion.id)


@login_required()
def flag_item(request, item_type, item_id, reason):
    """
    View that allows users to create a Flag object
    """
    messages.info(request, "Item flagged. Thank you for your help in keeping UnicornAttractor safe and fun for all")
    # if flagged item is a comment
    if item_type == "1":
        comment = get_object_or_404(Comment, id=int(item_id))
        flag = Flag(flagged_item_type=int(item_type), comment=comment,
                    flagged_by=request.user, reason=reason)
        flag.save()
        return redirect("view_suggestion", comment.suggestion.id)
    # if flagged item is a suggestion
    else:
        suggestion = get_object_or_404(Suggestion, id=item_id)
        flag = Flag(flagged_item_type=item_type, suggestion=suggestion,
                    flagged_by=request.user, reason=reason)
        flag.save()
        return redirect("view_suggestion", item_id)


@login_required()
def promote_feature(request):
    """
    Renders promote feature page where user can create
    a PromotedFeatureSuggestion object. Redirect to
    suggestions home if coins are not enabled. Users
    can be redirected to the store if they have insufficient
    coins to make a purchase
    """
    if settings.COINS_ENABLED:
        prices = get_feature_promotion_prices()
        user_coins = return_user_coins(request.user)
        coin_options = return_all_store_coin_options()
        discount_rates = get_promote_feature_discount_rates()

        tomorrow = (datetime.date.today() + datetime.timedelta(days=1))
        max_date = (get_voting_end_date() - datetime.timedelta(days=2))

        features = return_current_features()

        if request.method == "POST":
            if 'purchaseCoins' in request.POST:
                return purchase_coins_for_feature_promotion(request, user_coins, prices)

            else:
                submit_feature_promotion(request)
                price = prices["{}".format(request.POST.get("promotionDays"))]
                remove_coins(request.user, price, 9)
                messages.success(request, "Suggestion promoted. Thank you")

                return redirect("issue_tracker")

        return render(request, "promote_feature.html", {"features": features,
                                                        "user_coins": user_coins, "discount_rates": discount_rates,
                                                        "prices": prices, "coin_options": coin_options,
                                                        "max_date": max_date, "tomorrow": tomorrow})

    else:
        return redirect("issue_tracker")


def view_data(request):
    """
    Renders view_data page. June_completion_chart is rendered
    as an img from the S3 bucket. upvoted_chart and coin_spending_chart
    are rendered via HTML using current data
    """
    upvoted_chart = create_most_upvoted_chart(5)
    coin_spending_chart = create_coin_spending_chart()
    june_completions_chart_url = "https://s3-{0}.amazonaws.com/{1}/{2}/images/june_completions_chart.png".format(
        settings.AWS_S3_REGION_NAME, settings.AWS_STORAGE_BUCKET_NAME, settings.MEDIAFILES_LOCATION)
    return render(request, "view_data.html",
                  {"upvoted_chart": upvoted_chart, "coin_spending_chart": coin_spending_chart,
                   "june_completions_chart_url": june_completions_chart_url})


@login_required()
def render_flags_page(request):
    """
    Renders flags page. Redirects to suggestions
    home if user is not staff
    """
    if not request.user.is_staff:
        return redirect("issue_tracker")
    flags = Flag.objects.all()
    return render(request, "view_flags.html", {"flags": flags})


@login_required()
def flag_response(request, flag_id, result):
    """
    URL redirected to from flags page. Allows staff to change
    the 'result' value of a Flag object. Automatically sets
    this staff member as that Flag's responsible admin
    """
    if not request.user.is_staff:
        return redirect("issue_tracker")

    flag = get_object_or_404(Flag, id=flag_id)
    if result == "True":
        flag_result = True
    elif result == "False":
        flag_result = False
    else:
        flag_result = None
    flag.responsible_admin = request.user
    flag.result = flag_result
    flag.save()
    return redirect("flags")


@login_required()
def delete_comment(request, comment_id, suggestion_id):
    """
    Deletes the comment identified in the argument.
    Redirects to the suggestion identified in the argument
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        Comment.objects.filter(id=comment_id).delete()
        messages.success(request, "Comment deleted")
    return redirect("view_suggestion", suggestion_id)
