from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Count, Q
from datetime import datetime, timezone, timedelta
import math
from .forms import UserSignupForm, EmailLoginForm, UserSettingsForm
from apps.users.models import User
from apps.challenges.models import Challenge, Submission


def signup_view(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')    
            next_url = request.GET.get('next', 'course_list')
            return redirect(next_url)
    else:
        form = UserSignupForm()

    turnstile_site_key = getattr(settings, 'CF_TURNSTILE_SITE_KEY', '0x4AAAAAACXctAclxgTNx4Cl')

    return render(request, 'users/signup.html', {
        'form': form,
        'turnstile_site_key': turnstile_site_key
    })


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
            profile_form = UserSettingsForm(request.POST, request.FILES, instance=user)
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

def auth_success_view(request):
    """
    After successful social auth in a popup, this view is called.
    It renders a script that closes the popup and reloads the main window.
    """
    return render(request, 'users/auth_success.html')

def leaderboard_view(request):
    challenges = Challenge.objects.annotate(
        solvers_n=Count('submissions__submitted_by', filter=Q(submissions__status='accepted'), distinct=True)
    )
    challenge_scores = {}
    for c in challenges:
        n = c.solvers_n
        score = 100 if n == 0 else max(1, math.floor(100 - 10 * math.log2(n)))
        challenge_scores[c.id] = score

    period = request.GET.get('period', 'all')
    now = datetime.now(timezone.utc)
    
    submissions = Submission.objects.order_by('submitted_at')
    
    if period == 'day':
        submissions = submissions.filter(submitted_at__gte=now - timedelta(days=1))
    elif period == 'week':
        submissions = submissions.filter(submitted_at__gte=now - timedelta(days=7))
    elif period == 'month':
        submissions = submissions.filter(submitted_at__gte=now - timedelta(days=30))
        
    submissions = submissions.values(
        'submitted_by_id', 'challenge_id', 'status', 'submitted_at'
    )
    user_stats = {}
    for sub in submissions:
        uid = sub['submitted_by_id']
        cid = sub['challenge_id']
        status = sub['status']
        submitted_at = sub['submitted_at']
        
        if uid not in user_stats:
            user_stats[uid] = {
                'points': 0,
                'solved_challenges': set(),
                'total_considered_submissions': 0,
                'last_successful_time': None
            }
            
        stats = user_stats[uid]
        
        if cid in stats['solved_challenges']:
            continue
            
        stats['total_considered_submissions'] += 1
        
        if status == 'accepted':
            stats['solved_challenges'].add(cid)
            stats['points'] += challenge_scores.get(cid, 0)
            
            if stats['last_successful_time'] is None or submitted_at > stats['last_successful_time']:
                stats['last_successful_time'] = submitted_at

    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'points_desc')

    users = User.objects.filter(is_active=True)
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
        
    leaderboard = []
    
    max_dt = datetime.max.replace(tzinfo=timezone.utc)
    
    for user in users:
        stats = user_stats.get(user.id, {
            'points': 0,
            'solved_challenges': set(),
            'total_considered_submissions': 0,
            'last_successful_time': None
        })
        
        solved_count = len(stats['solved_challenges'])
        considered_count = stats['total_considered_submissions']
        acceptance_rate = (solved_count / considered_count * 100) if considered_count > 0 else 0
        acceptance_rate = int(round(acceptance_rate))
        last_time = stats['last_successful_time'] or max_dt
        
        leaderboard.append({
            'user': user,
            'points': stats['points'],
            'solved_count': solved_count,
            'acceptance_rate': acceptance_rate,
            'last_successful_time': last_time,
        })
        
    if sort_by == 'points_asc':
        leaderboard.sort(key=lambda x: (x['points'], x['solved_count'], x['acceptance_rate'], x['last_successful_time']))
    elif sort_by == 'solved_asc':
        leaderboard.sort(key=lambda x: (x['solved_count'], x['points'], x['acceptance_rate'], x['last_successful_time']))
    elif sort_by == 'solved_desc':
        leaderboard.sort(key=lambda x: (-x['solved_count'], -x['points'], -x['acceptance_rate'], x['last_successful_time']))
    elif sort_by == 'acceptance_asc':
        leaderboard.sort(key=lambda x: (x['acceptance_rate'], x['points'], x['solved_count'], x['last_successful_time']))
    elif sort_by == 'acceptance_desc':
        leaderboard.sort(key=lambda x: (-x['acceptance_rate'], -x['points'], -x['solved_count'], x['last_successful_time']))
    else: # points_desc is default
        leaderboard.sort(key=lambda x: (-x['points'], -x['solved_count'], -x['acceptance_rate'], x['last_successful_time']))

    return render(request, 'users/leaderboard.html', {
        'leaderboard': leaderboard,
        'search_query': search_query,
        'sort_by': sort_by,
        'period': period
    })

def profile_view(request, user_id):
    from django.shortcuts import get_object_or_404
    target_user = get_object_or_404(User, id=user_id)
    
    # Process submissions
    submissions = Submission.objects.filter(submitted_by=target_user)
    solved_ids = set(submissions.filter(status='accepted').values_list('challenge_id', flat=True))
    attempted_ids = set(submissions.exclude(status='accepted').values_list('challenge_id', flat=True))
    
    # Attempted means they have attempted but NOT solved it yet
    attempted_ids = attempted_ids - solved_ids
    
    # All challenges for github map
    challenges = Challenge.objects.all().order_by('id')
    
    activity_map = []
    for c in challenges:
        if c.id in solved_ids:
            state = 'solved'
        elif c.id in attempted_ids:
            state = 'attempted'
        else:
            state = 'unattempted'
            
        activity_map.append({
            'challenge': c,
            'state': state
        })
        
    context = {
        'target_user': target_user,
        'solved_count': len(solved_ids),
        'attempted_count': len(attempted_ids),
        'activity_map': activity_map,
    }
    return render(request, 'users/profile.html', context)