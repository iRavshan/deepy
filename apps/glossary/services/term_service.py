from ..models import Term
from django.contrib.postgres.search import TrigramSimilarity

class TermService:
    def get_by_slug(self, term_slug: str):
        try:
            return Term.objects.get(slug=term_slug)
        except Term.DoesNotExist:
            return None

    def get_all(self, search_query=None):
        queryset = Term.objects.all()
        
        if search_query:
            queryset = queryset.filter(term__icontains=search_query)
            
        return queryset
    
    def get_related_terms(self, term: Term):
        pass