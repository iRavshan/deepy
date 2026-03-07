from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Exists, OuterRef
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Challenge, Submission, Tag, Topic, SavedChallenge, ProgrammingLanguage
from .forms import ChallangeSubmissionForm
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from apps.users.utils import update_user_streak
from .utils.judge_service import judge_all_tests
import json



def challenge_list(request):
    challenges = Challenge.objects.all().select_related('topic').prefetch_related('tags')

    if request.user.is_authenticated:
        saved_subquery = SavedChallenge.objects.filter(
            user=request.user,
            challenge=OuterRef('pk')
        )
        accepted_subquery = Submission.objects.filter(
            submitted_by=request.user,
            challenge=OuterRef('pk'),
            status='accepted'
        )
        challenges = challenges.annotate(
            is_saved=Exists(saved_subquery),
            is_accepted=Exists(accepted_subquery)
        )

    search_query = request.GET.get('q', '')
    if search_query:
        challenges = challenges.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    difficulties = request.GET.getlist('difficulty')
    if difficulties:
        challenges = challenges.filter(difficulty__in=difficulties)


    selected_tags = request.GET.getlist('tag')
    if selected_tags:
        challenges = challenges.filter(tags__slug__in=selected_tags).distinct()

    all_tags = Tag.objects.all()

    context = {
        'tags': all_tags,
        'selected_difficulties': difficulties,
        'selected_tags': selected_tags,
        'search_query': search_query,
    }

    # Pagination
    paginator = Paginator(challenges, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context['challenges'] = page_obj

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('challenges/includes/challenge_list_partial.html', {'challenges': page_obj}, request=request)
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next()
        })

    return render(request, 'challenges/challenge_list.html', context)


def challenge_detail(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
    form = ChallangeSubmissionForm()
    
    next_challenge = Challenge.objects.filter(id__gt=challenge.id).order_by('id').first()
    prev_challenge = Challenge.objects.filter(id__lt=challenge.id).order_by('-id').first()

    languages = ProgrammingLanguage.objects.filter(is_active=True)

    context = {
        'challenge': challenge, 
        'form': form,
        'submissions': None,
        'next_challenge': next_challenge,
        'prev_challenge': prev_challenge,
        'languages': languages,
    }

    if request.user.is_authenticated:
        submissions = Submission.objects.filter(
            submitted_by=request.user, challenge=challenge
        ).select_related('language')
        context['submissions'] = submissions
    
    return render(request, 'challenges/challenge_detail.html', context)


def challenge_random(request):
    import random
    ids = list(Challenge.objects.values_list('slug', flat=True))
    if not ids:
        return redirect('challenge_list')
    random_slug = random.choice(ids)
    return redirect('challenge_detail', slug=random_slug)


def challenge_info(request):
    return render(request, 'challenges/challenge_info.html')


@login_required
@require_POST
def judge_submission_view(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
    code = request.POST.get('code')
    language_id = request.POST.get('language_id')
    
    # Get ProgrammingLanguage 
    lang = get_object_or_404(ProgrammingLanguage, judge0_id=language_id)
    
    result = judge_all_tests(
        source_code=code,
        language_id=int(language_id),
        test_cases=challenge.hidden_tests,
        cpu_time_limit=challenge.time_limit,
        memory_limit=challenge.memory_limit,
    )
    
    update_user_streak(request.user)
    
    submission = Submission.objects.create(
        challenge=challenge,
        submitted_by=request.user,
        code=code,
        language=lang,
        status=result['status_key'],
        execution_time=float(result['max_time']) if result.get('max_time') else None,
        memory_used=result.get('max_memory'),
    )

    # Add submission info to result for frontend
    result['submission'] = {
        'id': submission.id,
        'status': submission.get_status_display(),
        'status_key': submission.status,
        'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M'),
        'language': lang.name,
        'execution_time': result.get('max_time'),
        'memory_used': result.get('max_memory'),
    }
    
    return JsonResponse(result)

@login_required
@require_POST
def run_code_view(request, slug):    
    challenge = get_object_or_404(Challenge, slug=slug)
    code = request.POST.get('code')
    language_id = request.POST.get('language_id')
    
    result = judge_all_tests(
        source_code=code,
        language_id=int(language_id),
        test_cases=challenge.sample_tests,
        cpu_time_limit=challenge.time_limit,
        memory_limit=challenge.memory_limit,
    )
    
    return JsonResponse(result)

@login_required
@require_POST
def toggle_challenge_save(request):
    data = json.loads(request.body)
    slug = data.get('slug')
    
    challenge = get_object_or_404(Challenge, slug=slug)
    
    saved_challenge, created = SavedChallenge.objects.get_or_create(user=request.user, challenge=challenge)
    
    if not created:
        saved_challenge.delete()
        saved = False
    else:
        saved = True
        
    return JsonResponse({'saved': saved})