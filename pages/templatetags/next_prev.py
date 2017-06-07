from datetime import datetime
import traceback

from google.appengine.api import memcache
from google.appengine.ext import ndb

from django.template.defaultfilters import slugify
from django.template.defaulttags import cycle
from django.template import Library

from pages.models import Page, Archive, Tag


register = Library()

@register.simple_tag(takes_context = True)
def next_link(context, page_type, timestamp = None, pagenum = None) :
    '''
    This code smells too much like PHP
    '''
    if page_type == 'post' :
        try :
            page = Page.query().filter(
                            ndb.AND(Page.timestamp > int(timestamp),Page.blog == True, Page.draft == False)).order(Page.timestamp).fetch(1)
            page = page[0]
            return '<li style="float:right"><a href="/blog/archives/{0}">{1}&nbsp; &raquo;</a></li>'.format(
                            page.link, page.title
                        )
        except Exception , e:
            print e
            pass
        
    elif page_type == 'blog':
        
        try :
            if pagenum == 0 : 
                return ""
            pagenum = int(pagenum) -1
            
            page = Page.query().filter(
                            ndb.AND(Page.draft == False, Page.blog == True, Page.timestamp > int(timestamp))
                            ).order(Page.timestamp).fetch(1)
            page = page[0]
            
            #print page
            return '<li style="float:right"><a href="/blog/{0}">Newer entries&nbsp; &raquo;</a></li>'.format(
                            "page/%s/" % pagenum if pagenum > 1 else ""         
                        )
        except Exception , e:
            tb = traceback.format_exc()
            print tb
        
    return ""

@register.simple_tag(takes_context = True)
def prev_link(context, page_type, timestamp = 0, pagenum = None):
    if page_type == 'post' :
        try :
            page = Page.query().filter(
                            ndb.AND(Page.draft == False, Page.blog == True,  Page.timestamp < int(timestamp))).order(-Page.timestamp).fetch(1)
            page = page[0]
            return '<li style="float:left"><a href="/blog/archives/{0}">&laquo; &nbsp; {1}</a></li>'.format(
                            page.link, page.title
                        )
        except Exception , e:
            tb = traceback.format_exc()
            print tb

    elif page_type == 'blog':
        #print 'get prev (%s, %s)' % (timestamp, pagenum)
        try :
            page = Page.query().filter(
                            ndb.AND(Page.draft == False, Page.blog == True))
            if timestamp:
                page = page.filter(Page.timestamp > int(timestamp))
            page = page.order(Page.timestamp).fetch(1)[0]
            if page :
                if int(pagenum) :
                    prev = int(pagenum) + 1
                else :
                    prev = int(pagenum) + 2
    
                return '<li style="float:left"><a href="/blog/{0}">&laquo; &nbsp;Older entries</a></li>'.format(
                                "page/%s/" % prev if page else ""         
                        )
            else :
                return ''
        except Exception , e:
            tb = traceback.format_exc()
            print tb
            
    return ""


@register.simple_tag    
def tag_cloud(count = 25):
    '''
    Displays a tag cloud sidebar
    '''
    #print 'tag cloud'
    
    try:
        resp = memcache.get("tag_sidebar", None)
        if not resp :
            rows = []
            tags = Tag.query(projection = ['name','counter']).order(-Tag.counter).fetch(count)
            max = tags[0].counter or 1
            # the database fetch is based on the count(descending) once we
            # have it into python , we will convert to an alphabetical sort. 
            tags = sorted(tags , key = lambda p: p.name)
            
            for tag in  tags:
                rows.append('<a href="/blog/tag/%s/" style="font-size:%spx">%s</a>' % (slugify(tag.name[0]) ,
                                                    float(14) + (float(tag.counter)*8.6)/max, tag.name[0]   ))
        
            resp = " ".join(rows)
            
            memcache.set("tag_sidebar", resp)
        return resp;
    except Exception, e :
        print e
        return ""        
    
    
@register.simple_tag    
def archive_sidebar():
    try :
        archs = memcache.get("archive_sidebar", None)
        if not archs :
            rows = []
            for arch in Archive.query().order(-Archive.dt).fetch(20) : 
                rows.append('<li><a href="/blog/%d/%.2d/">%s %d</a></li>' % (arch.year, arch.month,
                                                datetime.strftime(arch.dt, '%B'), arch.year))
            
            result = "\n".join(rows)
            archs = '<ul class="list-unstyled">' +  result + '</ul>'
            memcache.set('archive_sidebar', archs)
            
        return archs
    except Exception, e:
        print e
        return ""
    
