from django.contrib.auth.views import LoginView

from .forms import LoginForm


class PhotoBankLoginView(LoginView):
    template_name = "gallery/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True