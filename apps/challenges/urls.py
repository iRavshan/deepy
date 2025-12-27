from django.urls import path
from .views import challenge_list, challenge_detail, challenge_by_tag, challenge_by_topic, judge_submission_view, search_challenges


urlpatterns = [
    path('', challenge_list, name='challenge_list'),
    path('<slug:slug>', challenge_detail, name='challenge_detail'),
    path('tag/<slug:slug>', challenge_by_tag, name='challenge_by_tag'),
    path('topic/<slug:slug>', challenge_by_topic, name='challenge_by_topic'),
    path('run_code/<slug:slug>', judge_submission_view, name='judge_submission'),
    path('search/', search_challenges, name='search_challenges'),
]
