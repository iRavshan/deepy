from django.urls import path
from .views import course_detail, lesson_detail, course_list, enroll_course, course_path

urlpatterns = [
    path("", course_list, name="course_list"),
    path("<slug:slug>", course_detail, name="course_detail"),
    path("<slug:course_slug>/lesson/<slug:lesson_slug>", lesson_detail, name="lesson_detail"),
    path("<slug:slug>/enroll", enroll_course, name="enroll_course"),
    path("<slug:slug>/path", course_path, name="course_path"),
]
