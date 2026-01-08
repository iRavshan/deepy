from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Challenge, Submission, Tag, Topic
from .forms import ChallangeSubmissionForm
from django.http import JsonResponse
from .utils.code_runners.python.python_judge import judge_submission



def challenge_list(request):
    challenges = Challenge.objects.all().select_related('topic').prefetch_related('tags')

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
        'challenges': challenges,
        'tags': all_tags,
        'selected_difficulties': difficulties,
        'selected_tags': selected_tags,
        'search_query': search_query,
    }

    return render(request, 'challenges/challenge_list.html', context)



def challenge_by_topic(request, slug):
    challenges = Challenge.objects.filter(topic__slug=slug)
    return render(request, 'challenges/challenge_by_topic.html', {'challenges': challenges,
                                                                  'tags': Tag.objects.all(),
                                                                  'topics': Topic.objects.all()})


def challenge_by_tag(request, slug):
    challenges = Challenge.objects.filter(tags__slug=slug)
    tag = get_object_or_404(Tag, slug=slug)
    return render(request, 'challenges/challenge_by_tag.html', {'challenges': challenges, 
                                                                'tag': tag})



def challenge_detail(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
    form = ChallangeSubmissionForm()
    
    context = {
        'challenge': challenge, 
        'form': form,
        'submissions': None
    }

    if request.user.is_authenticated:
        submissions = Submission.objects.filter(submitted_by=request.user, challenge=challenge)
        if submissions is not None:
            context['submissions'] = submissions
    
    return render(request, 'challenges/challenge_detail.html', context)


@login_required
@require_POST
def judge_submission_view(request, slug):
    challenge = Challenge.objects.get(slug=slug)
    code = request.POST.get('code')
    result = judge_submission(code, challenge.hidden_tests, challenge.time_limit)
    print(result)