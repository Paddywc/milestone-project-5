from market.coin_prices import suggestion_promotion_discounts as discounts
from market.coins import get_coins_price


def set_current_url_as_session_url(request):
    """
    """
    request.session["session_url"] = str(request.build_absolute_uri())


def retrieve_session_url(request):
    """
    """
    try:
        return request.session["session_url"]
    except:
        return False


def get_promote_feature_discount_rates():
    """
    """
    return {2: discounts.two, 3: discounts.three, 4: discounts.four, 5: discounts.five}


def get_feature_promotion_prices():
    """
    """
    price_of_one = get_coins_price("Feature Suggestion Promotion")

    def calculate_discounted_price(amount, percent_discount):
        total_value_before_discount = price_of_one * amount
        value_to_subtract = total_value_before_discount * (percent_discount / 100)
        value_with_discount = total_value_before_discount - value_to_subtract
        return int(value_with_discount)

    prices = {"1": price_of_one, "2": calculate_discounted_price(2, discounts.two),
              "3": calculate_discounted_price(3, discounts.three), "4": calculate_discounted_price(4, discounts.four),
              "5": calculate_discounted_price(5, discounts.five)}

    return prices
