from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Challenge, Submission, Tag, Topic
from .forms import ChallangeSubmissionForm
from django.http import JsonResponse
from .utils.code_runners.python.python_judge import judge_submission



def challenge_list(request):
    return render(request, 'challenges/challenge_list.html', {'challenges': Challenge.objects.all(), 
                                                              'tags': Tag.objects.all(),
                                                              'topics': Topic.objects.all()})

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
    return render(request, 'challenges/challenge_detail.html', {'challenge': challenge, 
                                                                'form': form})


@login_required
@require_POST
def judge_submission_view(request, slug):
    challenge = Challenge.objects.get(slug=slug)
    code = request.POST.get('code')
    result = judge_submission(code, challenge.hidden_tests, challenge.time_limit)
    print(result)