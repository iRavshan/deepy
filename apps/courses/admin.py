from django.contrib import admin
from . import models

admin.site.register(models.Course)
admin.site.register(models.Section)
admin.site.register(models.Lesson)
admin.site.register(models.GlossaryTerm)
admin.site.register(models.LearningDetail)
admin.site.register(models.Enrollment)
admin.site.register(models.LessonProgress)
admin.site.register(models.Quiz)
admin.site.register(models.Question)
admin.site.register(models.Answer)
admin.site.register(models.QuizAttempt)