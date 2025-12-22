from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Your Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password'
    }))


class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name']