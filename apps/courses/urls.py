from django.urls import path
from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("<slug:slug>", views.course_detail, name="course_detail"),
    path("<slug:course_slug>/lesson/<slug:lesson_slug>", views.lesson_detail, name="lesson_detail"),
    path("<slug:slug>/enroll", views.enroll_course, name="enroll_course"),
    path("<slug:slug>/path", views.course_path, name="course_path"),
    path("<slug:course_slug>/lesson/<slug:lesson_slug>/complete/", views.lesson_complete, name="lesson_complete"),
]
