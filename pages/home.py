import feedparser, re

from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import memcache

from django.utils.html import strip_tags
from django.shortcuts import render
from django.http.response import HttpResponse
from django.template.loader import render_to_string

from pages.models import Page
        
KEY_HOME_PAGE = "LAMP_HOME"
KEY_BLOG_MAIN = 'blog_MAIN'

def home(request):
    '''
    Home page will show the summary for the first three items + link for next seven.
    
    In addition to this, the old site shows the search results on the home page so
    that functionality also needs to be included.
    '''

    s = request.POST.get('s') or request.GET.get('s') 
    if s :
        index = search.Index(name="myIndex")
        query = search.Query(query_string = s)
        results = index.search(query)
        pages = []
        
        for r in results.results :
            fields = r.fields;
            page = {}
            for field in fields :

                if field.name == 'content' :
                    page['summary'] = strip_tags(field.value)
                else :
                    page[field.name] = field.value
                
                pages.append(page)
                
        return render(request, 'search.html', {'posts': pages})
    else :
        resp = None #memcache.get(KEY_HOME_PAGE, None)
        if not resp :
            d = feedparser.parse('http://photos.raditha.com/feed.rss')
            pics = memcache.get('foto-feed', None)  # @UndefinedVariable
            if not pics :
                pics = []
                for i in range(0,5) :
                    if i == 2 :
                        continue;
                    item = d['items'][i]
                    q = re.search('src ?= ?"(.*?)"', item['summary_detail']['value'])
                    pics.append({'img': q.group(1), 'link': item['link'] }) 
                
                memcache.set('foto-feed', pics)  # @UndefinedVariable
    
            pages = Page.query().filter( ndb.AND(Page.blog == True, Page.draft == False) ).order(-Page.timestamp).fetch(4)
            resp = render_to_string('home.html', {'pics': pics, 'posts': pages})
            
            memcache.set(KEY_HOME_PAGE, resp, 1800)
            
        return HttpResponse(resp)


def blog_main(request, page = 0):
    ''' 
    This is for the blog main page.
    '''
    resp =memcache.get(KEY_BLOG_MAIN + str(page), None)  # @UndefinedVariable
    if not resp :
        
        if page :
            page = int(page)
            pages = Page.query().filter( ndb.AND(Page.draft == False, Page.blog == True) ).order(-Page.timestamp).fetch(8, offset = ( (page-1)*8))
        else :
            pages = Page.query().filter( ndb.AND(Page.draft == False, Page.blog == True) ).order(-Page.timestamp).fetch(8)

        resp = render_to_string('blog_main.html',{'posts': pages, 'pagenum': page})
        
        memcache.set(KEY_BLOG_MAIN, resp)
        
    return HttpResponse(resp)

     
