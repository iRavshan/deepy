from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('user/', include('apps.users.urls')),
    path('courses/', include('apps.courses.urls')),
    path('challenges/', include('apps.challenges.urls')),
    path('glossary/', include('apps.glossary.urls')),
    path('accounts/', include('allauth.urls')),
]

handler404 = 'config.views.custom_404'
handler500 = 'config.views.custom_500'
handler403 = 'config.views.custom_403'
handler400 = 'config.views.custom_400'