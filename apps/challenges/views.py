import tempfile
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from pathlib import Path
from .models import Challenge, Submission, Tag, Topic
from .forms import ChallangeSubmissionForm
import docker
from django.http import JsonResponse
from services.code_executor import CodeExecutor


def challenge_list(request):
    return render(request, 'challenges/challenge_list.html', {"challenges": Challenge.objects.all(), 
                                                              "tags": Tag.objects.all(),
                                                              "topics": Topic.objects.all()})

def challenge_by_topic(request, slug):
    challenges = Challenge.objects.filter(topic__slug=slug)
    return render(request, 'challenges/challenge_by_topic.html', {"challenges": challenges,
                                                                  "tags": Tag.objects.all(),
                                                                  "topics": Topic.objects.all()})


def challenge_by_tag(request, slug):
    challenges = Challenge.objects.filter(tags__slug=slug)
    tag = get_object_or_404(Tag, slug=slug)
    return render(request, 'challenges/challenge_by_tag.html', {"challenges": challenges, "tag": tag})



def challenge_detail(request, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
    form = ChallangeSubmissionForm()
    return render(request, 'challenges/challenge_detail.html', {'challenge': challenge, 'form': form})


@login_required
def run_code_in_docker(request, slug):
    challenge = Challenge.objects.get(slug=slug)

    if request.method == "POST":
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        if not code:
            return JsonResponse({
                'success': False,
                'error': 'No code provided',
                'output': ''
            })
        # Basic validation
        if len(code) > 10000:  # Limit code size
            return JsonResponse({
                'success': False,
                'error': 'Code too long (max 10000 characters)',
                'output': ''
            })
    
        # Execute code
        executor = CodeExecutor()
        result = executor.execute_code(code, language)
        
        return JsonResponse(result)

    return JsonResponse({"error": "Only POST allowed"})