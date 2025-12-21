from pyexpat.errors import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Lesson, Course, Enrollment
from .selectors import list_courses, get_course_by_slug, get_lesson_by_slug
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def course_list(request):
    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(user=request.user)
        enrolled_course_ids = enrollments.values_list('course__id', flat=True)
        courses = Course.objects.filter(id__in=enrolled_course_ids)
        unenrolled_courses = Course.objects.exclude(id__in=enrolled_course_ids)
        return render(request, 'courses/course_list.html', {'enrolled_courses': courses, 'unenrolled_courses': unenrolled_courses})
    else:
        courses = list_courses()
        return render(request, 'courses/course_list.html', {'courses': courses})

    
def course_detail(request, slug):
    course = get_course_by_slug(slug)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    return render(request, 'courses/course_detail.html', {'course': course, 'is_enrolled': is_enrolled})


@require_POST
@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        return redirect('course_path', slug=course.slug)
    else:
        messages.info(request, "You are already enrolled in this course.")


def course_path(request, slug):
    course = get_course_by_slug(slug)
    return render(request, 'courses/course_path.html', {'course': course})


def lesson_detail(request, course_slug, lesson_slug):
    lesson = get_lesson_by_slug(lesson_slug=lesson_slug)
    return render(request, 'courses/lesson_detail.html', {'lesson': lesson})

