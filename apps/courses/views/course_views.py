from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from ..repositories.course_repository import CourseRepository
from ..services.enrollment_service import EnrollmentService
from ..services.progress_service import ProgressService
from apps.glossary.services.term_service import TermService


def course_list(request):
    course_repo = CourseRepository()
    if request.user.is_authenticated:
        enrolled_courses = course_repo.get_enrolled_courses(request.user)
        unenrolled_courses = course_repo.get_unenrolled_courses(request.user)
    else:
        enrolled_courses = []
        unenrolled_courses = course_repo.get_all()
    
    context = {
        'enrolled_courses': enrolled_courses,
        'unenrolled_courses': unenrolled_courses
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    course_repo = CourseRepository()
    course = course_repo.get_with_details(slug)
    context = {'course': course, 'is_enrolled': False}

    if request.user.is_authenticated:
        enrollment_service = EnrollmentService()
        is_enrolled = enrollment_service.is_enrolled(request.user, course)
        context['is_enrolled'] = is_enrolled
        
    return render(request, 'courses/course_detail.html', context)

    
@login_required
@require_POST
def course_enroll(request, slug):
    enrollment_service = EnrollmentService()
    course_repo = CourseRepository()

    course = course_repo.get_by_field(slug=slug)
    enrollment_service.enroll(request.user, course)

    return redirect('course_path', slug=slug)


def course_path(request, slug):
    course_repo = CourseRepository()
    course = course_repo.get_with_sections(slug)
    term_service = TermService()
    
    # Get random glossary term
    random_term = term_service.get_all().order_by('?').first()
    
    # Calculate total lessons
    total_lessons = sum(section.lessons.count() for section in course.sections.all())
    
    context = {
        'course': course,
        'course_percentage': 0,
        'completed_lessons': [],
        'random_term': random_term,
        'total_lessons': total_lessons,
        'lessons_completed': 0,
    }

    if request.user.is_authenticated:
        progress_service = ProgressService()
        course_percentage = progress_service.get_course_percentage(request.user, course.id)
        completed_lessons_ids = progress_service.get_completed_lessons(request.user, course.id)
        context['course_percentage'] = course_percentage
        context['completed_lessons'] = completed_lessons_ids
        context['lessons_completed'] = len(completed_lessons_ids)

    return render(request, 'courses/course_path.html', context)