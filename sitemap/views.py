from google.appengine.ext import ndb
from pages.models import Page, Tag
from django.shortcuts import render
from django.template.context import RequestContext


def main(request):
    pages = Page.query().filter(Page.draft == False).order(-Page.timestamp)
    tags = Tag.query()
    
    return render(request, 'sitemap.xml',{'pages': pages, 'tags': tags},
                        context_instance = RequestContext(request), content_type='text/xml' )