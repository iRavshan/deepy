from ..models import Term
from django.contrib.postgres.search import TrigramSimilarity

class TermService:
    def get_by_slug(self, term_slug: str):
        try:
            return Term.objects.get(slug=term_slug)
        except Term.DoesNotExist:
            return None
        
    def get_all(self):
        return Term.objects.all()
    
    def get_related_terms(self, term: Term):
        pass