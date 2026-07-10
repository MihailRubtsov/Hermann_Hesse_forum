from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import generic

from .forms import StyledLoginForm, StyledSignUpForm


class SignUpView(generic.CreateView):
    form_class = StyledSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class StyledLoginView(LoginView):
    authentication_form = StyledLoginForm
    redirect_authenticated_user = True
