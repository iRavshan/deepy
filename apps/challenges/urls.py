from django.urls import path
from .views import challenge_list, challenge_detail, run_code_view, challenge_random, judge_submission_view



urlpatterns = [
    path('', challenge_list, name='challenge_list'),
    path('<slug:slug>/', challenge_detail, name='challenge_detail'),
    path('<slug:slug>/run/', run_code_view, name='run_code'),
    path('random/', challenge_random, name='challenge_random'),
    path('<slug:slug>/judge_submission/', judge_submission_view, name='judge_submission'),
]
