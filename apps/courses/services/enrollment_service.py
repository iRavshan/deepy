from ..repositories.enrollment_repository import EnrollmentRepository

class EnrollmentService:
    def __init__(self):
        self.enrollment_repo = EnrollmentRepository()

    def enroll(self, user, course):
        return self.enrollment_repo.enroll(user, course)
    
    def is_enrolled(self, user, course):
        return self.enrollment_repo.is_enrolled(user, course)