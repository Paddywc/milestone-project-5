from .views import create_user

urlpatterns = [
    url(r'^signup/$', create_user, name='signup')
    ]