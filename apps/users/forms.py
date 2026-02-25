from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django_cf_turnstile.fields import TurnstileCaptchaField
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
    cf_turnstile = TurnstileCaptchaField()


class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name']

class UserSettingsForm(forms.ModelForm):
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Ismingiz'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Familiyangiz'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email manzil'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']