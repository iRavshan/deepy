from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.courses.models import Course
from apps.challenges.models import Challenge

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'course_list', 'challenge_list', 'glossary']

    def location(self, item):
        return reverse(item)

class CourseSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Course.objects.all()

class ChallengeSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return Challenge.objects.all()
