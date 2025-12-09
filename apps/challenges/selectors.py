from .models import Exercise

def get_exercises_for_course(course_id: int):
    return Exercise.objects.filter(course_id=course_id).order_by("id")

def get_exercise_detail(exercise_id: int):
    return Exercise.objects.select_related("course").get(id=exercise_id)