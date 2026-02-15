from django.contrib import admin
from . import models

from nested_admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline

admin.site.register(models.Course)
admin.site.register(models.Section)
admin.site.register(models.Lesson)
admin.site.register(models.LearningDetail)
admin.site.register(models.Enrollment)
admin.site.register(models.LessonProgress)
admin.site.register(models.QuizAttempt)

class AnswerInline(NestedTabularInline):
    model = models.Answer
    extra = 1

class QuestionInline(NestedStackedInline):
    model = models.Question
    extra = 1
    inlines = [AnswerInline]

class QuizAdmin(NestedModelAdmin):
    inlines = [QuestionInline]
    list_display = ('lesson',)
    search_fields = ('lesson__title',)

admin.site.register(models.Quiz, QuizAdmin)