def retrieve_session_url(request):
    """
    """
    try:
        return request.session["session_url"]
    except:
        return False