from django.contrib import admin
from .models import Challenge, Submission, Tag, Hint, Topic, ProgrammingLanguage

admin.site.register(Challenge)
admin.site.register(Submission)  
admin.site.register(Topic)

@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'judge0_id', 'monaco_identifier', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("name",)}
    search_fields = ["name"]

@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    list_display = ["challenge", 'order']
    list_filter = ["challenge"]
    ordering = ["challenge", 'order']