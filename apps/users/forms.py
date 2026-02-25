from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django_cf_turnstile.fields import TurnstileCaptchaField
from .models import User

class EmailLoginForm(forms.Form):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Your Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password'
    }))
    cf_turnstile = TurnstileCaptchaField()

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            from django.contrib.auth import authenticate
            # Pass email=email to avoid FieldError('username') in allauth backend
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Bunday elektron pochta yoki parol noto'g'ri. Iltimos, ma'lumotlarni tekshirib qayta kiriting.",
                    code='invalid_login',
                )
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


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