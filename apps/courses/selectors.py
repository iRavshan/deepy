from typing import Optional, Tuple
from django.db.models import QuerySet, Prefetch, Count 
from django.shortcuts import get_object_or_404
from .models import Course, Section, Lesson, Enrollment


def list_courses() -> QuerySet[Course]:
    return Course.objects.all()


def get_course_by_slug(slug: str) -> Course:
    return Course.objects.filter(slug=slug).prefetch_related(
        Prefetch('sections', queryset=Section.objects.order_by('order').prefetch_related(
            Prefetch('lessons', queryset=Lesson.objects.order_by('order'))
        ))).annotate(lesson_count = Count('sections__lessons')).first()


def get_section_lessons(section: Section) -> QuerySet[Lesson]:
    return section.lessons.all()


def get_lesson_by_slug(lesson_slug: str) -> Lesson:
    return get_object_or_404(Lesson, slug=lesson_slug)


def get_enrollment(user, course) -> Optional[Enrollment]:
    return Enrollment.objects.filter(user=user, course=course).first()


def get_or_create_enrollment(user, course) -> Tuple[Enrollment, bool]:
    return Enrollment.objects.get_or_create(user=user, course=course)


#def get_lesson_progress(enrollment: Enrollment, lesson: Lesson) -> Optional[LessonProgress]:
    #return LessonProgress.objects.filter(enrollment=enrollment, lesson=lesson).first()


def list_user_enrollments(user) -> QuerySet[Enrollment]:
    return Enrollment.objects.filter(user=user).select_related("course")


#def list_completed_lessons(enrollment: Enrollment) -> QuerySet[LessonProgress]:
    #return enrollment.lesson_progresses.filter(is_completed=True)
