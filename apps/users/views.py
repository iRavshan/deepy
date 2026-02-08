from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UserSignupForm, EmailLoginForm
import requests


def verify_turnstile(token, request):
    if not token:
        return False
    
    secret_key = settings.CF_TURNSTILE_SECRET_KEY
    if not secret_key:
        return False
    
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_address:
        ip_address = ip_address.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    # Verify with Cloudflare API
    verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    data = {
        'secret': secret_key,
        'response': token,
        'remoteip': ip_address
    }
    
    try:
        response = requests.post(verify_url, data=data, timeout=5)
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        print(f"Turnstile verification error: {e}")
        return False


def signup_view(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)    
            return redirect('course_list')
    else:
        form = UserSignupForm()

    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = EmailLoginForm(request, data=request.POST)
        
        turnstile_token = request.POST.get('cf-turnstile-response')
        if not verify_turnstile(turnstile_token, request):
            form.add_error(None, "Captcha verification failed. Please try again.")
            return render(request, "users/login.html", {
                'form': form,
                'turnstile_site_key': settings.CF_TURNSTILE_SITE_KEY
            })
        
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), 
                                password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
                return redirect('course_list')
    else:
        form = EmailLoginForm()

    return render(request, "users/login.html", {
        'form': form,
        'turnstile_site_key': settings.CF_TURNSTILE_SITE_KEY
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')