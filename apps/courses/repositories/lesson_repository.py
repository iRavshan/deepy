from typing import Optional
from ..models import Lesson
from .base_repository import BaseRepository

class LessonRepository(BaseRepository[Lesson]):
    def __init__(self):
        super().__init__(Lesson)

    def get_by_id(self, id) -> Optional[Lesson]:
        return super().get_by_id(id)
    
    def get_by_slug(self, course_slug: str, lesson_slug: str) -> Optional[Lesson]:
        try:
            return Lesson.objects.select_related(
                'section', 
                'section__course'
            ).get(
                slug=lesson_slug,
                section__course__slug=course_slug
            )
        except Lesson.DoesNotExist:
            return None