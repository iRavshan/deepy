from django.urls import path
from .views.course_views import course_list, course_detail, course_enroll, course_path
from .views.lesson_views import lesson_detail, lesson_quiz

urlpatterns = [
    path("", course_list, name="course_list"),
    path("<slug:slug>", course_detail, name="course_detail"),
    path("<slug:slug>/enroll", course_enroll, name="course_enroll"),
    path("<slug:slug>/path", course_path, name="course_path"),
    path("<slug:course_slug>/lesson/<slug:lesson_slug>", lesson_detail, name="lesson_detail"),
    path("<slug:course_slug>/lesson/<slug:lesson_slug>/quiz", lesson_quiz, name="lesson_quiz"),
]