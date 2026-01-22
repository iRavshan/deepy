from django.apps import AppConfig
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):
        from .models import User
        from .utils import update_user_streak

        @receiver(user_logged_in)
        def on_user_logged_in(sender, user, request, **kwargs):
            update_user_streak(user)