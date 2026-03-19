from django.conf.urls import handler400, handler403, handler404, handler500
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from django.conf.urls.i18n import i18n_patterns
from config.sitemaps import StaticViewSitemap, CourseSitemap, ChallengeSitemap
from . import views

sitemaps = {
    'static': StaticViewSitemap,
    'courses': CourseSitemap,
    'challenges': ChallengeSitemap,
}

# Non-prefixed URLs (language-independent resources)
urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('humans.txt', TemplateView.as_view(template_name='humans.txt', content_type='text/plain')),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('llms.txt', TemplateView.as_view(template_name='llms.txt', content_type='text/plain')),
    path('.well-known/security.txt', TemplateView.as_view(template_name='.well-known/security.txt', content_type='text/plain')),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Language-prefixed URLs (e.g. /en/, /uz/, /ru/)
urlpatterns += i18n_patterns(
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('user/', include('apps.users.urls')),
    path('courses/', include('apps.courses.urls')),
    path('challenges/', include('apps.challenges.urls')),
    path('deepwiki/', include('apps.glossary.urls')),
    path('accounts/', include('allauth.urls')),
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('_nested_admin/', include('nested_admin.urls')),
    prefix_default_language=True,
)

handler404 = 'config.views.custom_404'
handler500 = 'config.views.custom_500'
handler403 = 'config.views.custom_403'
handler400 = 'config.views.custom_400'