from typing import List, Optional
from django.db.models import Prefetch, Count
from ..models import Course, Section, Lesson
from .base_repository import BaseRepository

class CourseRepository(BaseRepository[Course]):
    def __init__(self):
        super().__init__(Course)

    def get_by_id(self, id) -> Optional[Course]:
        return super().get_by_id(id)
    
    def get_by_field(self, **kwargs) -> Optional[Course]:
        return super().get_by_field(**kwargs)
    
    def get_all(self) -> List[Course]:
        return Course.objects.all()
    
    def get_enrolled_courses(self, user) -> Optional[List[Course]]:
        return Course.objects.filter(enrollments__user=user)
                    
    def get_unenrolled_courses(self, user) -> Optional[List[Course]]:
        return Course.objects.exclude(enrollments__user=user)
    
    def get_with_details(self, slug: str):
        try:
            return Course.objects.prefetch_related(
                Prefetch(
                    'sections',
                    queryset=Section.objects.prefetch_related(
                        Prefetch(
                            'lessons',
                            queryset=Lesson.objects.select_related('quiz').order_by('order')
                        )
                    ).order_by('order')
                )
            ).annotate(
                sections_count=Count('sections', distinct=True),
                lessons_count=Count('sections__lessons', distinct=True),
                quizzes_count=Count('sections__lessons__quiz', distinct=True)
            ).get(slug=slug)
            
        except Course.DoesNotExist:
            return None
        
    def get_with_sections(self, slug: str):
        try:
            return Course.objects.prefetch_related(
                Prefetch(
                    'sections',
                    queryset=Section.objects.prefetch_related(
                        Prefetch(
                            'lessons',
                            queryset=Lesson.objects.prefetch_related(
                                'quiz' 
                            ).order_by('order')
                        )
                    ).order_by('order')
                )
            ).get(slug=slug)
            
        except Course.DoesNotExist:
            return None