from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from config.sitemaps import StaticViewSitemap, CourseSitemap, ChallengeSitemap
from . import views

sitemaps = {
    'static': StaticViewSitemap,
    'courses': CourseSitemap,
    'challenges': ChallengeSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('user/', include('apps.users.urls')),
    path('courses/', include('apps.courses.urls')),
    path('challenges/', include('apps.challenges.urls')),
    path('deepwiki/', include('apps.glossary.urls')),
    path('accounts/', include('allauth.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('_nested_admin/', include('nested_admin.urls')),
]

handler404 = 'config.views.custom_404'
handler500 = 'config.views.custom_500'
handler403 = 'config.views.custom_403'
handler400 = 'config.views.custom_400'