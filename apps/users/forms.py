from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django_cf_turnstile.fields import TurnstileCaptchaField
from .models import User

class EmailLoginForm(forms.Form):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Elektron pochta'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Parol'
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
            from allauth.account.models import EmailAddress
            from django.conf import settings
            
            self.user_cache = authenticate(self.request, email=email, password=password)
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Elektron pochta yoki parol noto'g'ri. Iltimos, ma'lumotlarni tekshirib qayta kiriting.",
                    code='invalid_login',
                )
                
            # Check allauth email verification status
            if getattr(settings, 'ACCOUNT_EMAIL_VERIFICATION', 'none') == 'mandatory':
                email_address = EmailAddress.objects.filter(user=self.user_cache, email__iexact=email).first()
                if not email_address or not email_address.verified:
                    raise forms.ValidationError(
                        "Ushbu elektron pochta tasdiqlanmagan. Iltimos, elektron pochtangizga habardorni tasdiqlang."
                    )
                    
        return self.cleaned_data

    def get_user(self):
        return self.user_cache



class UserSignupForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ismingiz'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Parol'}))
    cf_turnstile = TurnstileCaptchaField()
    
    class Meta:
        model = User
        fields = ['first_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Elektron pochta'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserSettingsForm(forms.ModelForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Foydalanuvchi nomi'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Ismingiz'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Familiyangiz'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email manzil'}))
    age = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Yoshingiz'}))
    linkedin_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/username'}))
    github_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'https://github.com/username'}))
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'age', 'linkedin_url', 'github_url', 'profile_picture']