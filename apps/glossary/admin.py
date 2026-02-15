from django.contrib import admin
from .models import Term, Topic


from modeltranslation.admin import TranslationAdmin

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'description', 'term_count']
    search_fields = ['name', 'description']
    
    def term_count(self, obj):
        return obj.terms.count()
    term_count.short_description = 'Number of Terms'


@admin.register(Term)
class TermAdmin(TranslationAdmin):
    list_display = ['term', 'topic', 'short_definition']
    list_filter = ['topic']
    search_fields = ['term', 'short_definition', 'definition']
    list_select_related = ['topic']
    
    group_fieldsets = True # Groups translations by field type
    
    # We don't need to manually exclude 'term' etc because TranslationAdmin
    # handles the form construction, but if we want to be explicit:
    # exclude = ('term', 'short_definition', 'definition')
    # However, usually just using TranslationAdmin is enough to make the UX better (tabbed or grouped).
    # Let's try group_fieldsets = True which makes it much cleaner (tabs).