from django.contrib import admin
from .models import Course, Lesson, Section, GlossaryTerm, LearningDetail, Enrollment

admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Lesson)
admin.site.register(GlossaryTerm)
admin.site.register(LearningDetail)
admin.site.register(Enrollment)