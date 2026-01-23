from django.shortcuts import render
from .services.term_service import TermService

def glossary_view(request):
    term_service = TermService()
    search_query = request.GET.get('search')
    topic_slug = request.GET.get('topic')
    
    context = {
        'terms': term_service.get_all(search_query=search_query, topic_slug=topic_slug),
        'topics': term_service.get_all_topics(),
        'search_query': search_query,
        'selected_topic': topic_slug,
    }
    return render(request, 'glossary/glossary.html', context)

def term_view(request, slug):
    term_service = TermService()
    term = term_service.get_by_slug(slug)
    context = {
        'term': term,
        'related_terms': term_service.get_related_terms(term)
    }
    return render(request, 'glossary/term.html', context)

def speed_run_view(request):
    term_service = TermService()
    context = {
        'terms': term_service.get_all()
    }
    return render(request, 'glossary/speed_run.html', context)

def learning_view(request):
    term_service = TermService()
    context = {
        'terms': term_service.get_all()
    }
    return render(request, 'glossary/learning_mode.html', context)