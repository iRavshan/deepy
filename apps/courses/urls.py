from django.urls import path
from .views import course_detail, lesson_detail, course_list

urlpatterns = [
    path("", course_list, name="course_list"),
    path("<slug:slug>", course_detail, name="course_detail"),
    path("<slug:course_slug>/lesson/<slug:lesson_slug>", lesson_detail, name="lesson_detail"),
]
