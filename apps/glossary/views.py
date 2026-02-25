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

def speed_run_setup_view(request):
    term_service = TermService()
    context = {
        'topics': term_service.get_all_topics()
    }
    return render(request, 'glossary/speed_run_setup.html', context)

def speed_run_view(request):
    term_service = TermService()
    
    # Get parameters
    topic_slugs = request.GET.getlist('topics')
    mode = request.GET.get('mode', 'survival')
    start_side = request.GET.get('side', 'term')
    duration = request.GET.get('duration', '60')
    
    # Filter terms
    terms = term_service.get_all()
    
    if topic_slugs and 'all' not in topic_slugs:
        terms = terms.filter(topic__slug__in=topic_slugs)
        
    # Always shuffle for Speed Run
    terms = terms.order_by('?')
        
    # Serialize terms for JS
    terms_data = []
    for term in terms:
        terms_data.append({
            'id': term.id,
            'term': term.term,
            'term_en': getattr(term, 'term_en', ''),
            'definition': term.short_definition,
            'topic': term.topic.name if term.topic else 'General',
        })
    
    context = {
        'terms_json': json.dumps(terms_data),
        'start_side': start_side,
        'mode': mode,
        'duration': duration,
        'total_count': terms.count()
    }
    return render(request, 'glossary/speed_run.html', context)

def learning_setup_view(request):
    term_service = TermService()
    context = {
        'topics': term_service.get_all_topics()
    }
    return render(request, 'glossary/learning_setup.html', context)

def learning_view(request):
    term_service = TermService()
    
    # Get parameters
    topic_slugs = request.GET.getlist('topics')
    order = request.GET.get('order', 'random')
    start_side = request.GET.get('side', 'term')
    
    # Filter terms
    terms = term_service.get_all()
    
    if topic_slugs and 'all' not in topic_slugs:
        terms = terms.filter(topic__slug__in=topic_slugs)
        
    if order == 'random':
        terms = terms.order_by('?')
    else:
        terms = terms.order_by('term')
        
    # Serialize terms for JS
    terms_data = []
    for term in terms:
        terms_data.append({
            'id': term.id,
            'term': term.term,
            'term_en': getattr(term, 'term_en', ''),
            'definition': term.short_definition,
            'full_definition': term.definition,
            'topic': term.topic.name if term.topic else 'General',
            'slug': term.slug
        })
    
    context = {
        'terms_json': json.dumps(terms_data),
        'start_side': start_side,
        'total_count': terms.count()
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