from ..models import Enrollment, Course
from .base_repository import BaseRepository


class EnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self):
        super().__init__(model=Enrollment)

    def enroll(self, user, course: Course) -> Enrollment:
        enrollment, created = Enrollment.objects.get_or_create(
            user=user, 
            course=course
        )
        return enrollment

    def is_enrolled(self, user, course: Course) -> bool:
        if not user.is_authenticated:
            return False
            
        return Enrollment.objects.filter(user=user, course=course).exists()