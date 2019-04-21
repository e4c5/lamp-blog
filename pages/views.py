import datetime, time
import traceback
import re

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.conf import settings
from django.utils import feedgenerator
from django.shortcuts import render

from django.template.loader import render_to_string
from django.template.context import RequestContext
from slugify import slugify

from google.appengine.ext import ndb
from google.appengine.api import memcache

from potatopage.paginator import GaeNdbPaginator

from pages.models import Page, Tag, Archive


def get_page_from_cache(request):
    try:
        key = request.get_full_path() + request.flavour
    except:
        key = request.get_full_path()

    resp = memcache.get(key, None)  # @UndefinedVariable
    if resp:
        return HttpResponse(resp)
    else:
        return None


def send_response(request, response):
    memcache.set(request.get_full_path() + request.flavour, response)  # @UndefinedVariable
    return HttpResponse(response)


def posts_tagged(request, slug):
    '''
    Shows the stuff for a given tag
    '''
    resp = get_page_from_cache(request)
    if not resp:
        tag = Tag.get_by_id(slugify(slug))

        pages = Page.query().filter(
            Page.tags.IN(tag.name)).order(-Page.timestamp)
        resp = render_to_string('tag.html', {'posts': pages, 'tag': tag},
                                )
        return send_response(request, resp)

    return resp


def archives(request, year=None, month=None, day=None, page=None):
    '''
    Archives is a bit tricky before there are all, yearly and monthly archives
    '''
    resp = get_page_from_cache(request)
    if not resp:  
        if year == None:
            pages = []
            for arch in Archive.query().order(-Archive.dt) : 
                pages.append('<li><a href="/blog/%d/%.2d/">%s %d</a></li>' % (arch.year, arch.month,
                                                datetime.datetime.strftime(arch.dt, '%B'), arch.year))
            n = len(pages)
            if n % 2 :
                part1 = pages[0:n/2+1]
                part2 = pages[n/2+1:]
    
            else :
                part1 = pages[0:n/2]
                part2 = pages[n/2:]
                
            return render(request, 'archives.html', 
                                  {'posts': [part1, part2] } )
            
        else :
            year = int(year)
            
            if month :
                month = int(month)
                # archives for a whole month. Finding the end of the month is 
                # tricky.
                dt_start = datetime.date(year, month, 1)
                if month == 12 :
                    dt_end = datetime.date(year +1 , 1, 1)
                else :
                    dt_end = datetime.date(year, month+1, 1)
            else : 
                # yearly archives.
                dt_start = datetime.date(year, 1, 1)
                dt_end = datetime.date(year + 1, 1, 1)
            
            pages = Page.query().filter( 
                            ndb.AND( Page.timestamp >= int(time.mktime(dt_start.timetuple()) * 1000) ,
                                     Page.timestamp < int(time.mktime(dt_end.timetuple()) * 1000),
                                     Page.draft == False )
                                      ).order(-Page.timestamp)
            
            if month :
                month = datetime.datetime.strftime(dt_start, '%B')
        
        paginator = GaeNdbPaginator(
            pages,
            per_page=settings.ITEMS_PER_PAGE,
            batch_size=2)
        pagenum = request.GET.get('page', 1)
        resp = render(request, 'archives.html',
                                  {'posts': paginator.page(pagenum),
                                   'pagenum': pagenum,
                                   'year': year,
                                   'month': month,
                                   'day': day},
                                  )
        return send_response(request, resp)

    return resp


def catch_all(request, slug):
    '''
    This is kind of like the index.php router in wordpress. We will also do a 
    'found' (302) redirect when the url does not end in a trailing slash. Of 
    course this does not apply to urls that end with .php .html etc, etc
    '''
    try :
        resp = memcache.get(request.path, None)
        if not resp:    
            if request.path.endswith('/') or re.search('\.(php|txt|html|txt)$', request.path):
                p = Page.query(ndb.OR(Page.link == slug, Page.link == slug + "/")).fetch(1)[0]
                nxt = Page.query(projection=['link','title']).filter(Page.timestamp > p.timestamp).fetch(1)
                prev = Page.query(projection=['link','title']).filter(Page.timestamp < p.timestamp).fetch(1)
            else :
                return HttpResponseRedirect(request.path + '/', )
                
            resp = render_to_string(p.template or 'blog-post.html', 
                                      {'page': p, 'next': nxt, 'prev': prev })
        
        return HttpResponse(resp)
    except Exception:
        if re.search('index.php$', slug) :
            slug = re.sub('index.php$','',slug)
            return HttpResponseRedirect('/' + slug)
        
        slug = re.sub('blog/archives/','',slug)
        return blog_catch_all(request, slug)


def blog_catch_all(request, slug):
    '''
    This is kind of like the index.php router in wordpress 
    '''
    resp = memcache.get(request.path, None)  # @UndefinedVariable

    if not resp:    
        try :
            
            p = Page.query(ndb.OR(Page.link == slug, Page.link == slug + "/")).fetch(1)[0]
            next = Page.query(projection=['link','title']).filter(Page.timestamp > p.timestamp).fetch(1)
            prev = Page.query(projection=['link','title']).filter(Page.timestamp < p.timestamp).fetch(1)
            
            resp = render_to_string(p.template or 'blog-post.html', 
                                      {'page': p, 'next': next, 'prev': prev })
            
            memcache.set(request.path, resp)
            
            return HttpResponse(resp)
        except Exception, e:
            tb = traceback.format_exc()
            print tb
            raise Http404
    
    else :
        return HttpResponse(resp)


def tags(request):
    '''
    This is the main page for the tags
    '''
    content = get_page_from_cache(request)
    if content :
        return content
    else :
        return send_response(request, render_to_string('tags.html', {'tags': Tag.query()}))
        
    

def rss(request):
    '''
    Generates an RSS feed
    '''
    resp = memcache.get('rss_feed', None)  # @UndefinedVariable
    if not resp:
        feed = feedgenerator.Rss201rev2Feed(title= "The Site With The LAMP",
            link="http://raditha.com/",
            description = "A long standing but irregularly updated tech blog",
            author_name="Raditha dissanayake", 
            feed_url="http://raditha.com/feed")
    
        for page in Page.query().filter(Page.blog == True).filter(Page.draft == False).order(-Page.timestamp).fetch(20):
            feed.add_item(title = page.title,
                link = "http://raditha.com/blog/archives/{0}".format(page.link, page.title),                
                pubDate = page.published_at,
                description  = page.content)
        resp = feed.writeString('UTF-8')
        memcache.set('rss_feed', resp)  # @UndefinedVariable
        
    response = HttpResponse(resp, mimetype='application/xml')
    return response
