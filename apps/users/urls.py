from django.urls import path
from .views import login_view, signup_view, logout_view, settings_view, bookmarks_view, auth_success_view, leaderboard_view, profile_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('settings/', settings_view, name='settings'),
    path('bookmarks/', bookmarks_view, name='bookmarks'),
    path('auth-success/', auth_success_view, name='auth_success'),
    path('rating/', leaderboard_view, name='rating'),
    path('profile/<int:user_id>/', profile_view, name='profile'),
]
