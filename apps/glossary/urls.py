from django.urls import path
from .views import (
    glossary_view, term_view, speed_run_view, learning_view,
    random_term_json, toggle_term_save, learning_setup_view,
    speed_run_setup_view, team_mode_setup_view, team_mode_view
)

urlpatterns = [
    path("", glossary_view, name="glossary"),
    path("term/<slug:slug>", term_view, name="term"),
    path("mode/speed-run", speed_run_view, name="speed_run"),
    path("mode/speed-run/setup", speed_run_setup_view, name="speed_run_setup"),
    path("mode/learning", learning_view, name="learning"),
    path("mode/learning/setup", learning_setup_view, name="learning_setup"),
    path("mode/team", team_mode_view, name="team_mode"),
    path("mode/team/setup", team_mode_setup_view, name="team_mode_setup"),
    path("api/random-term/", random_term_json, name="random_term_api"),
    path("api/toggle-save/", toggle_term_save, name="toggle_term_save"),
]
