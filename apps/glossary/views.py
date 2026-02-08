import json
from django.shortcuts import render
from django.http import JsonResponse
from .services.term_service import TermService

from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef
from .models import SavedTerm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef
from .models import SavedTerm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def glossary_view(request):
    term_service = TermService()
    search_query = request.GET.get('search')
    topic_slug = request.GET.get('topic')
    
    all_terms = term_service.get_all(search_query=search_query, topic_slug=topic_slug)
    
    # Annotate with is_saved for the current user
    if request.user.is_authenticated:
        saved_subquery = SavedTerm.objects.filter(
            user=request.user,
            term=OuterRef('pk')
        )
        all_terms = all_terms.annotate(is_saved=Exists(saved_subquery))
    
    # Pagination
    paginator = Paginator(all_terms, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # AJAX Handler for Infinite Scroll
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('glossary/includes/term_list_partial.html', {'terms': page_obj}, request=request)
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None
        })

    context = {
        'terms': page_obj, # Pass page_obj instead of all terms
        'topics': term_service.get_all_topics(),
        'search_query': search_query,
        'selected_topic': topic_slug,
    }
    return render(request, 'glossary/glossary.html', context)

@login_required
@require_POST
def toggle_term_save(request):
    data = json.loads(request.body)
    slug = data.get('slug')
    
    term_service = TermService()
    term = term_service.get_by_slug(slug)
    
    saved_term, created = SavedTerm.objects.get_or_create(user=request.user, term=term)
    
    if not created:
        saved_term.delete()
        saved = False
    else:
        saved = True
        
    return JsonResponse({'saved': saved})

def term_view(request, slug):
    term_service = TermService()
    term = term_service.get_by_slug(slug)
    
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedTerm.objects.filter(user=request.user, term=term).exists()

    context = {
        'term': term,
        'related_terms': term_service.get_related_terms(term),
        'is_saved': is_saved
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


def random_term_json(request):
    term_service = TermService()
    term = term_service.get_all().order_by('?').first()
    if term:
        data = {
            'term': term.term,
            'definition': term.short_definition,
            'slug': term.slug
        }
    else:
        data = {}
    return JsonResponse(data)