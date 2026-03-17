from celery import shared_task
from django.core.cache import cache
from .models import Submission, Challenge
from apps.users.utils import update_user_streak
from .utils.judge_service import batch_judge_tests

@shared_task
def process_submission_task(submission_id, code, language_id, test_cases, time_limit, memory_limit, user_id=None):
    try:
        submission = Submission.objects.get(id=submission_id)
    except Submission.DoesNotExist:
        return None

    result = batch_judge_tests(
        source_code=code,
        language_id=language_id,
        test_cases=test_cases,
        cpu_time_limit=time_limit,
        memory_limit=memory_limit,
    )

    submission.status = result['status_key']
    submission.execution_time = float(result['max_time']) if result.get('max_time') else None
    submission.memory_used = result.get('max_memory')
    submission.save()

    if user_id:
        from apps.users.models import User
        try:
            user = User.objects.get(id=user_id)
            update_user_streak(user)
        except User.DoesNotExist:
            pass

    # Add DB fields back for frontend
    result['submission'] = {
        'id': submission.id,
        'status': submission.get_status_display(),
        'status_key': submission.status,
        'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M'),
        'language': submission.language.name,
        'execution_time': result.get('max_time'),
        'memory_used': result.get('max_memory'),
    }

    # Cache the extensive JSON output by submission_id so we don't clog DB
    cache.set(f"submission_detail_{submission.id}", result, timeout=86400) # 1 day
    return submission.id

@shared_task
def process_run_code_task(task_uuid, code, language_id, test_cases, time_limit, memory_limit):
    # This task is just for "Run Code" where it doesn't save to DB.
    # We reference it by a random UUID locally generated.
    result = batch_judge_tests(
        source_code=code,
        language_id=language_id,
        test_cases=test_cases,
        cpu_time_limit=time_limit,
        memory_limit=memory_limit,
    )
    
    cache.set(f"run_code_detail_{task_uuid}", result, timeout=86400)
    return task_uuid
