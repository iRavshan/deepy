from typing import Optional, List
from django.utils import timezone
from ..models import LessonProgress, Lesson
from .base_repository import BaseRepository

class ProgressRepository(BaseRepository[LessonProgress]):
    def __init__(self):
        super().__init__(LessonProgress)

    def get_for_user(self, user, lesson: Lesson) -> Optional[LessonProgress]:
        if not user.is_authenticated:
            return None    
        try:
            return LessonProgress.objects.get(user=user, lesson=lesson)
        except LessonProgress.DoesNotExist:
            return None

    def mark_complete(self, user, lesson: Lesson) -> LessonProgress:
        progress, created = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson
        )

        if not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()
            
        return progress

    def get_completed_lessons_count(self, user, course_id: int) -> int:
        if not user.is_authenticated:
            return 0
            
        return LessonProgress.objects.filter(
            user=user,
            lesson__section__course_id=course_id, # Optimization: Filter by Course ID
            completed=True
        ).count()

    def get_completed_lesson_ids(self, user, course_id: int) -> List[int]:
        if not user.is_authenticated:
            return []

        return list(
            LessonProgress.objects.filter(
                user=user,
                lesson__section__course_id=course_id,
                completed=True
            ).values_list('lesson_id', flat=True)
        )

    