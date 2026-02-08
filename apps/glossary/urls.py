from django.urls import path
from .views import glossary_view, term_view, speed_run_view, learning_view, random_term_json, toggle_term_save

urlpatterns = [
    path("", glossary_view, name="glossary"),
    path("term/<slug:slug>", term_view, name="term"),
    path("mode/speed-run", speed_run_view, name="speed_run"),
    path("mode/learning", learning_view, name="learning"),
    path("api/random-term/", random_term_json, name="random_term_api"),
    path("api/toggle-save/", toggle_term_save, name="toggle_term_save"),
]