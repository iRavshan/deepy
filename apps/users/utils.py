from django.utils import timezone
from datetime import timedelta

def update_user_streak(user):
    """
    Updates the user's streak based on their last activity date.
    Should be called when the user performs a significant action (login, submission, etc).
    """
    today = timezone.localdate()
    
    if user.last_activity_date == today:
        return # Already counted for today

    if user.last_activity_date == today - timedelta(days=1):
        # Streak continues
        user.current_streak += 1
    else:
        # Streak broken (or first time)
        user.current_streak = 1
        
    # Update max streak
    if user.current_streak > user.max_streak:
        user.max_streak = user.current_streak
        
    user.last_activity_date = today
    user.save(update_fields=['current_streak', 'max_streak', 'last_activity_date'])
