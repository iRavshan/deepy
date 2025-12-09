from django.shortcuts import render
from .models import Lesson
from .selectors import list_courses, get_course_by_slug, get_lesson_by_slug
from django.contrib.auth.decorators import login_required

@login_required
def course_list(request):
    courses = list_courses()
    return render(request, 'courses/course_list.html', {"courses": courses})

def course_detail(request, slug):
    course = get_course_by_slug(slug)
    return render(request, 'courses/course_detail.html', {'course': course})

def lesson_detail(request, course_slug, lesson_slug):
    lesson = get_lesson_by_slug(lesson_slug=lesson_slug)
    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
    })
