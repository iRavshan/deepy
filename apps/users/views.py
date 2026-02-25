from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UserSignupForm, EmailLoginForm, UserSettingsForm


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
        
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'course_list')
                return redirect(next_url)
    else:
        form = EmailLoginForm()

    turnstile_site_key = getattr(settings, 'CF_TURNSTILE_SITE_KEY', '0x4AAAAAACXctAclxgTNx4Cl')

    return render(request, "users/login.html", {
        'form': form,
        'turnstile_site_key': turnstile_site_key
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def settings_view(request):
    user = request.user
    profile_form = UserSettingsForm(instance=user)
    password_form = PasswordChangeForm(user)

    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'profile_update':
            profile_form = UserSettingsForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Shaxsiy ma\'lumotlar muvaffaqiyatli saqlandi!')
                return redirect('settings')
        
        elif action == 'password_update':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important to keep user logged in!
                messages.success(request, 'Parol muvaffaqiyatli yangilandi!')
                return redirect('settings')

    return render(request, 'users/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })


@login_required
def bookmarks_view(request):
    try:
        from apps.challenges.models import SavedChallenge
        saved_challenges = SavedChallenge.objects.filter(user=request.user).select_related('challenge', 'challenge__topic')
    except ImportError:
        saved_challenges = []
        
    try:
        from apps.glossary.models import SavedTerm
        saved_terms = SavedTerm.objects.filter(user=request.user).select_related('term')
    except ImportError:
        saved_terms = []

    return render(request, 'users/bookmarks.html', {
        'saved_challenges': saved_challenges,
        'saved_terms': saved_terms
    })