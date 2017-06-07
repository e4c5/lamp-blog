from pages.views import get_page_from_cache, send_response
from faqs.models import Faq

from django.http import  Http404
from django.template.loader import render_to_string

from pages.models import Tag


def catch_all(request, slug):
    '''
    This is kind of like the index.php router in wordpress but for FAQ entries 
    '''
    resp = get_page_from_cache(request)
    
    try :
        if not resp:
            tag = Tag.get_by_id(slug)
            
            pages = Faq.query().filter(Faq.tags.IN( tag.name )).order(-Faq.priority)
            resp = render_to_string('faq.html', {'posts': pages, 'tag': tag })
            
            return send_response(request, resp)
            
        return resp
    except Exception, ex :
        print ex
        raise Http404