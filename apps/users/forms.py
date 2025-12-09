from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email']