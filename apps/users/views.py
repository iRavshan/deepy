from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserSignupForm, EmailLoginForm


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
            user = authenticate(username=form.cleaned_data.get('username'), 
                                password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
                return redirect('course_list')
    else:
        form = EmailLoginForm()

    return render(request, "users/login.html", {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')