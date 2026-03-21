from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.files.base import ContentFile
import requests


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter that populates user profile fields (name, avatar)
    when signing up via Google or GitHub.
    """

    def populate_user(self, request, sociallogin, data):
        """Called during signup to fill in user fields from provider data."""
        user = super().populate_user(request, sociallogin, data)
        
        # Ensure first_name and last_name are populated
        if not user.first_name:
            user.first_name = data.get('first_name', '')
        if not user.last_name:
            user.last_name = data.get('last_name', '')
        
        return user

    def save_user(self, request, sociallogin, form=None):
        """Called after user creation — download and save avatar."""
        user = super().save_user(request, sociallogin, form)
        self._save_avatar(user, sociallogin)
        return user

    def _save_avatar(self, user, sociallogin):
        """Download the profile picture from the social provider and save it."""
        if user.profile_picture:
            return  # Don't overwrite existing picture
        
        avatar_url = None
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        if provider == 'google':
            avatar_url = extra_data.get('picture')
        elif provider == 'github':
            avatar_url = extra_data.get('avatar_url')

        if avatar_url:
            try:
                response = requests.get(avatar_url, timeout=10)
                if response.status_code == 200:
                    # Determine extension
                    content_type = response.headers.get('content-type', 'image/png')
                    ext = 'jpg' if 'jpeg' in content_type else 'png'
                    filename = f"social_{provider}_{user.id}.{ext}"
                    user.profile_picture.save(filename, ContentFile(response.content), save=True)
            except Exception:
                pass  # Silently fail — avatar is optional
