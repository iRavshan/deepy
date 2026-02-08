from django.urls import path
from .views import challenge_list, challenge_detail, run_code_view


urlpatterns = [
    path('', challenge_list, name='challenge_list'),
    path('<slug:slug>/', challenge_detail, name='challenge_detail'),
    path('<slug:slug>/run/', run_code_view, name='run_code'),
]
