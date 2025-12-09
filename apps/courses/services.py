from typing import Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .models import Course, Section, Lesson, Enrollment, LessonProgress
from . import selectors


@transaction.atomic
def enroll_user(user, course: Course) -> Enrollment:
    """
    Enroll a user into a course.
    Creates Enrollment and initial LessonProgress rows (optional).
    Returns the Enrollment object.
    """
    enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)

    if created:
        # Create LessonProgress rows for each lesson (initially not completed)
        lessons = Lesson.objects.filter(section__course=course).order_by("section__order", "order")
        bulk = []
        for lesson in lessons:
            bulk.append(LessonProgress(enrollment=enrollment, lesson=lesson))
        if bulk:
            LessonProgress.objects.bulk_create(bulk)
    return enrollment


@transaction.atomic
def unenroll_user(user, course: Course) -> None:
    """
    Unenroll user: deletes Enrollment and progress related to that course.
    Use carefully.
    """
    enrollment = selectors.get_enrollment(user, course)
    if not enrollment:
        return
    # Depending on business rules, you may want to archive instead of deleting
    enrollment.lesson_progresses.all().delete()
    enrollment.delete()


def is_user_enrolled(user, course: Course) -> bool:
    return Enrollment.objects.filter(user=user, course=course).exists()


def update_last_accessed(enrollment: Enrollment) -> None:
    enrollment.last_accessed = timezone.now()
    enrollment.save(update_fields=["last_accessed"])


def compute_course_progress(enrollment: Enrollment) -> float:
    """
    Computes percentage progress for a given enrollment.
    Returns float between 0 and 100.
    """
    total = enrollment.lesson_progresses.count()
    if total == 0:
        return 0.0
    completed = enrollment.lesson_progresses.filter(is_completed=True).count()
    return round((completed / total) * 100, 1)


@transaction.atomic
def mark_lesson_completed(user, course: Course, lesson: Lesson) -> LessonProgress:
    """
    Mark a lesson as completed for a user. Creates enrollment if missing.
    Returns the updated LessonProgress object.
    """
    enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)

    # Ensure Lesson belongs to the Course
    if lesson.section.course_id != course.id:
        raise PermissionDenied("Lesson does not belong to this course")

    lp, created = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)

    if not lp.is_completed:
        lp.is_completed = True
        lp.completed_at = timezone.now()
        lp.save(update_fields=["is_completed", "completed_at"])
    # Update enrollment last_accessed
    update_last_accessed(enrollment)

    # Optionally update course completed flag
    progress = compute_course_progress(enrollment)
    if progress >= 100:
        enrollment.is_completed = True
        enrollment.save(update_fields=["is_completed"])
    return lp


def get_next_incomplete_lesson(enrollment: Enrollment) -> Optional[Lesson]:
    """
    Returns the next incomplete lesson for the user's enrollment.
    """
    next_lp = enrollment.lesson_progresses.filter(is_completed=False).order_by("lesson__section__order", "lesson__order").first()
    return next_lp.lesson if next_lp else None


def get_resume_lesson(enrollment: Enrollment) -> Optional[Lesson]:
    """
    Return the best lesson to resume: the first incomplete lesson or last completed.
    """
    next_lesson = get_next_incomplete_lesson(enrollment)
    if next_lesson:
        return next_lesson
    # if all completed, return last lesson
    last_completed = enrollment.lesson_progresses.filter(is_completed=True).order_by("-completed_at").first()
    return last_completed.lesson if last_completed else None


@transaction.atomic
def mark_section_completed_if_needed(enrollment: Enrollment, section: Section) -> None:
    """
    If all lessons in a section are completed, optionally set a flag or award XP.
    """
    # Example: award XP or badge. Placeholder for gamification hooks.
    lessons = section.lessons.all()
    completed_count = enrollment.lesson_progresses.filter(lesson__in=lessons, is_completed=True).count()
    if completed_count == lessons.count():
        # TODO: award badge or emit signal
        pass


# Utility: course overview DTO
def get_user_course_overview(user, course: Course) -> dict:
    """
    Returns a serializable dict used by templates:
    {
      "course": Course,
      "enrolled": bool,
      "progress": 12.5,
      "next_lesson": Lesson or None,
      "sections": [
         {"section": Section, "lessons": [
             {"lesson": Lesson, "is_completed": True/False}
         ]}
      ]
    }
    """
    enrolled = selectors.get_enrollment(user, course) is not None
    enrollment = selectors.get_enrollment(user, course) if enrolled else None
    progress = compute_course_progress(enrollment) if enrollment else 0.0
    next_lesson = get_resume_lesson(enrollment) if enrollment else None

    sections_data = []
    sections = course.sections.all().order_by("order")
    for sec in sections:
        lessons_info = []
        lessons = sec.lessons.all().order_by("order")
        for lesson in lessons:
            is_done = False
            if enrollment:
                lp = selectors.get_lesson_progress(enrollment, lesson)
                is_done = bool(lp and lp.is_completed)
            lessons_info.append({"lesson": lesson, "is_completed": is_done})
        sections_data.append({"section": sec, "lessons": lessons_info})

    return {
        "course": course,
        "enrolled": bool(enrollment),
        "progress": progress,
        "next_lesson": next_lesson,
        "sections": sections_data,
    }
