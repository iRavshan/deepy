from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Challenge, Submission, Tag, Topic
from .forms import ChallangeSubmissionForm
from django.http import JsonResponse
from .utils.code_runners.python_runner import run_code


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
def judge_submission(request, slug):
    challenge = Challenge.objects.get(slug=slug)

    form = ChallangeSubmissionForm(request, data=request.POST)

    if form.is_valid():
        code = form.cleaned_data.get('code')
        print(code) 
