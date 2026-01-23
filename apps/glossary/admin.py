from django.contrib import admin
from .models import Term, Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'description', 'term_count']
    search_fields = ['name', 'description']
    
    def term_count(self, obj):
        return obj.terms.count()
    term_count.short_description = 'Number of Terms'


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['term', 'topic', 'short_definition']
    list_filter = ['topic']
    search_fields = ['term', 'short_definition', 'definition']
    list_select_related = ['topic']