from django.shortcuts import render
from .services.term_service import TermService

def glossary_view(request):
    term_service = TermService()
    context = {
        'terms': term_service.get_all()
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