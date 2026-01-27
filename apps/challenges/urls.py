from django.urls import path
from .views import challenge_list, challenge_detail, judge_submission_view, challenge_random, run_code_view


urlpatterns = [
    path('', challenge_list, name='challenge_list'),
    path('random/', challenge_random, name='challenge_random'),
    path('<slug:slug>', challenge_detail, name='challenge_detail'),
    path('run_code/<slug:slug>', judge_submission_view, name='judge_submission'),
    path('test_code/<slug:slug>', run_code_view, name='run_code'),
]
