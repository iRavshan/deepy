from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Exists, OuterRef, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce, NullIf
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Challenge, Submission, Tag, SavedChallenge, ProgrammingLanguage
from .forms import ChallangeSubmissionForm
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from .tasks import process_submission_task, process_run_code_task
import json
import uuid



def challenge_list(request):
    challenges = Challenge.objects.all().select_related('topic').prefetch_related('tags')

    total_challenges = Challenge.objects.count()
    solved_challenges_count = 0

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
        solved_challenges_count = Submission.objects.filter(
            submitted_by=request.user,
            status='accepted'
        ).values('challenge').distinct().count()

    progress_percentage = int((solved_challenges_count / total_challenges * 100)) if total_challenges > 0 else 0

    search_query = request.GET.get('q', '')
    if search_query:
        challenges = challenges.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )



    selected_tags = request.GET.getlist('tag')
    if selected_tags:
        challenges = challenges.filter(tags__slug__in=selected_tags).distinct()

    sort_param = request.GET.get('sort', '')
    if sort_param:
        challenges = challenges.annotate(
            solvers_n=Count('submissions__submitted_by', filter=Q(submissions__status='accepted'), distinct=True),
            total_subs=Count('submissions'),
            accepted_subs=Count('submissions', filter=Q(submissions__status='accepted')),
            acc_rate=Coalesce(
                ExpressionWrapper(
                    F('accepted_subs') * 100.0 / NullIf(F('total_subs'), 0),
                    output_field=FloatField()
                ),
                0.0
            )
        )
        if sort_param == 'points_asc':
            challenges = challenges.order_by('-solvers_n', '-id')
        elif sort_param == 'points_desc':
            challenges = challenges.order_by('solvers_n', 'id')
        elif sort_param == 'solved_asc':
            challenges = challenges.order_by('solvers_n', 'id')
        elif sort_param == 'solved_desc':
            challenges = challenges.order_by('-solvers_n', '-id')
        elif sort_param == 'acceptance_asc':
            challenges = challenges.order_by('acc_rate', 'id')
        elif sort_param == 'acceptance_desc':
            challenges = challenges.order_by('-acc_rate', '-id')
    else:
        challenges = challenges.order_by('id')

    all_tags = Tag.objects.all()

    context = {
        'tags': all_tags,
        'selected_tags': selected_tags,
        'search_query': search_query,
        'sort_by': sort_param,
        'total_challenges': total_challenges,
        'solved_challenges_count': solved_challenges_count,
        'progress_percentage': progress_percentage,
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
    
    lang = get_object_or_404(ProgrammingLanguage, judge0_id=language_id)
    
    submission = Submission.objects.create(
        challenge=challenge,
        submitted_by=request.user,
        code=code,
        language=lang,
        status='pending',
    )
    
    process_submission_task.delay(
        submission_id=submission.id,
        code=code,
        language_id=int(language_id),
        test_cases=challenge.hidden_tests,
        time_limit=challenge.time_limit,
        memory_limit=challenge.memory_limit,
        user_id=request.user.id
    )
    
    return JsonResponse({'status': 'processing', 'submission_id': submission.id})

@login_required
@require_POST
def run_code_view(request, slug):    
    challenge = get_object_or_404(Challenge, slug=slug)
    code = request.POST.get('code')
    language_id = request.POST.get('language_id')
    
    task_uuid = str(uuid.uuid4())
    process_run_code_task.delay(
        task_uuid=task_uuid,
        code=code,
        language_id=int(language_id),
        test_cases=challenge.sample_tests,
        time_limit=challenge.time_limit,
        memory_limit=challenge.memory_limit,
    )
    
    return JsonResponse({'status': 'processing', 'task_uuid': task_uuid})

@login_required
@require_POST
def check_submission_status(request):
    data = json.loads(request.body)
    submission_id = data.get('submission_id')
    task_uuid = data.get('task_uuid')
    
    from django.core.cache import cache
    if submission_id:
        result = cache.get(f"submission_detail_{submission_id}")
    elif task_uuid:
        result = cache.get(f"run_code_detail_{task_uuid}")
    else:
        return JsonResponse({"error": "No ID provided"})
        
    if result:
        return JsonResponse(result)
    else:
        return JsonResponse({'status': 'processing'})

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