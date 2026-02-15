from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from ..repositories import LessonRepository, CourseRepository, ProgressRepository


def lesson_detail(request, course_slug, lesson_slug):
    lesson_repo = LessonRepository()
    course_repo = CourseRepository()

    lesson = lesson_repo.get_by_slug(course_slug, lesson_slug)
    course = course_repo.get_by_field(slug=course_slug)

    context = {
        'lesson': lesson,   
        'course': course,
        'completed_lessons': [],
    }

    if request.user.is_authenticated:
        progress_repo = ProgressRepository()
        completed_lessons = progress_repo.get_completed_lesson_ids(request.user, course.id)
        context['completed_lessons'] = completed_lessons

    return render(request, 'courses/lesson_detail.html', context)


def lesson_quiz(request, course_slug, lesson_slug):
    lesson_repo = LessonRepository()
    course_repo = CourseRepository()

    lesson = lesson_repo.get_by_slug(course_slug, lesson_slug)
    course = course_repo.get_by_field(slug=course_slug)
    
    if not hasattr(lesson, 'quiz'):
        return redirect('lesson_detail', course_slug=course_slug, lesson_slug=lesson_slug)

    context = {
        'lesson': lesson,   
        'course': course,
        'quiz': lesson.quiz,
    }

    return render(request, 'courses/lesson_quiz.html', context)