from ..repositories.progress_repository import ProgressRepository
from ..models import Lesson

class ProgressService:
    def __init__(self):
        self.progress_repo = ProgressRepository()

    def get_course_percentage(self, user, course_id):
        # 1. Get total lessons in course (Fast count)
        total_lessons = Lesson.objects.filter(section__course_id=course_id).count()
        
        if total_lessons == 0:
            return 0

        # 2. Get completed count using our new Repo method
        completed_count = self.progress_repo.get_completed_lessons_count(user, course_id)

        # 3. Calculate Math
        return int((completed_count / total_lessons) * 100)
    
    def get_completed_lessons(self, user, course_id):
        return self.progress_repo.get_completed_lesson_ids(user, course_id)