from ..models import Term, Topic
from django.contrib.postgres.search import TrigramSimilarity

class TermService:
    def get_by_slug(self, term_slug: str):
        try:
            return Term.objects.select_related('topic').get(slug=term_slug)
        except Term.DoesNotExist:
            return None

    def get_all(self, search_query=None, topic_slug=None):
        queryset = Term.objects.select_related('topic').all()
        
        if topic_slug:
            queryset = queryset.filter(topic__slug=topic_slug)
        
        if search_query:
            queryset = queryset.filter(term__icontains=search_query)
            
        return queryset
    
    def get_all_topics(self):
        return Topic.objects.all()
    
    def get_topic_by_slug(self, topic_slug: str):
        try:
            return Topic.objects.get(slug=topic_slug)
        except Topic.DoesNotExist:
            return None
    
    def get_related_terms(self, term: Term):
        pass