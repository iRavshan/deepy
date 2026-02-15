from modeltranslation.translator import register, TranslationOptions
from .models import Term

@register(Term)
class TermTranslationOptions(TranslationOptions):
    fields = ('term', 'short_definition', 'definition')
