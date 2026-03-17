from django.urls import path
from .views import challenge_list, challenge_detail, run_code_view, challenge_random, judge_submission_view, toggle_challenge_save, challenge_info, check_submission_status

urlpatterns = [
    path('', challenge_list, name='challenge_list'),
    path('toggle-save/', toggle_challenge_save, name='toggle_challenge_save'),
    path('random/', challenge_random, name='challenge_random'),
    path('info/', challenge_info, name='challenge_info'),
    path('check_status/', check_submission_status, name='check_submission_status'),
    path('<slug:slug>/', challenge_detail, name='challenge_detail'),
    path('<slug:slug>/run/', run_code_view, name='run_code'),
    path('<slug:slug>/judge_submission/', judge_submission_view, name='judge_submission'),
]
