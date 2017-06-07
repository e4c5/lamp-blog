import datetime
import json
import traceback
import time
from django.http.response import HttpResponse
from pages.models import Page

def legacy_importer(request):
    '''
    This endpoint is to import from legacy websites and blogs
    '''
    if request.method == 'POST' :
        data = json.loads(request.POST.get('data'))
        if request.POST.get('campfire') == 'hey, this is JuAt RanDOM keY to PROTECT GAints attacks Q(!ZOIE/.kl' :
            # this is one off, intended to be run on the local development server only.
            # doesn't need much security because of that. Don't use in production.
            
            try:
                if request.POST.get('content') == 'update' :

                    p = Page.query(Page.link == data['slug'] + "/").fetch(1)[0]
                    p.summary = data['description'][:500]
                    p.published_at = datetime.datetime.strptime(data['published_at'], '%Y-%m-%d %H:%M:%S')
                    p.timestamp = int(time.mktime(p.published_at.utctimetuple())) * 1000
                    p.template = data['layout']
                    p.put()

                elif request.POST.get('content') == 'corrections' :
                    #print "Corrections", data
                    for b in data:
                        print b

                else :
                    if data.get('postdate') :
                        dt = datetime.datetime.strptime(data['postdate'], '%Y-%m-%d %H:%M:%S')
                        print data['link']
                        p = Page(title = data['title'], link = data['link'], published_at = dt,
                             blog = True, draft = data['draft'], template = 'blog-post.html',
                             content = data['content'], tags = data.get('tags',[]),
                             alt_link = data['alt_link'],
                             summary = data['summary'], categories = data.get('categories',[]))
                    else :
                        p = Page(title = data['title'], link = data['link'],
                             blog = False, draft = False, template = 'page.html',
                             content = data['content'], summary = data['summary'])

                    p.put()
            except Exception, e:
                tb = traceback.format_exc()
                print tb


    else :
        print 'get'
    return HttpResponse('ok')


