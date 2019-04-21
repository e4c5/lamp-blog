import datetime, time
import re
import random
import traceback

from django.utils.html import strip_tags
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect

from google.appengine.ext import ndb
from google.appengine.api import users, memcache, search

from slugify import slugify

from pages.forms import PageForm, FaqForm
from pages.models import Page, Tag, Archive
from faqs.models import Faq
from potatopage.paginator import GaeNdbPaginator

from pages.settings import AUTHORIZED_EMAILS


def is_authorized_user():
    u = users.get_current_user()
    if (u and u.email() in AUTHORIZED_EMAILS) or users.is_current_user_admin():
        return True
    else :
        return False

def unix_timestamp(dt):
    return int(time.mktime(dt.utctimetuple())*1000)

def rebuild_tags(request):
    '''
    Building a tag page is not fun because GQL doesn't do COUNT GROUP BY.

    Work around is to have the count in a separate table which can be
    updated whenever a new post is added
    '''
    if is_authorized_user():
        for tag in Tag.query() :
            #tag.counter = 0
            #tag.name = []
            #tag.put()
            tag.key.delete()
            pass

        pages = Page.query(projection=['tags'])
        for page in pages:
            for tag in page.tags :
                update_tag(tag)
        return HttpResponse('ok')
    else :
        return HttpResponse("<a href='{}'>login</a>". format(users.create_login_url('/rebuild-tags/')))


def update_tag(tag):
    try :
        item = Tag.get_or_insert(slugify(tag))
        if tag == 'Python' or tag == 'python':
            print item, slugify(tag)

        if not item.name :
            item.name = [tag]
        else :
            if not tag in item.name :
                item.name.append(tag)
        item.counter += 1
        item.put()
    except Exception, e :
        print e
        pass


def rebuild_sidebar(request):
    '''
    Rebuilds the archive sidebar
    '''
    if is_authorized_user():
        pages = Page.query().filter(Page.blog == True)
        for page in pages:
            #if not page.timestamp :
            page.timestamp = unix_timestamp(page.published_at)
            if page.link.endswith('/') :
                page.link = page.link[:-1]

            page.put()

            update_archive(page)
        return HttpResponse('ok')
    else :
        return HttpResponse("<a href='{}'>login</a>". format(users.create_login_url('/')))


def update_archive(page):
    ''' See that an archive entry is created for this page '''
    key = ndb.Key('Archive',"{0}/{1}".format(page.published_at.year , page.published_at.month))
    arch = key.get()

    if not arch:
        dt = datetime.date(page.published_at.year, page.published_at.month, 1)
        arch = Archive(key = key, dt = dt,
                       year = page.published_at.year, month = page.published_at.month)
        arch.put()

        memcache.delete('archive_sidebar');


def editor(request, slug = None):
    if request.GET.get('type') == 'faq' or request.POST.get('type') == 'faq':
        return edit_faq(request, slug)
    else :
        return edit_page(request, slug)


def edit_faq(request, slug):
    '''
    This is where we edit an old FAQ entry or create a new one
    '''
    if is_authorized_user():
        faq = None
        if request.method == 'GET' :
            if slug :
                try :
                    faq = memcache.get("/faqitem/{0}".format(slug))  # @UndefinedVariable
                    if not faq :
                        faq = Faq.query(Faq.slug == slug).get()
                    if not faq :
                        key = ndb.Key(urlsafe = slug)
                        faq = key.get()

                    p = faq.to_dict()

                    p['tags'] = ",".join(p['tags'])
                    p['key'] = faq.key.id()
                    if p.get('published_at') :
                        p.pop('published_at')

                    form = FaqForm(data = p)
                except:
                    tb = traceback.format_exc()
                    print tb
                    raise Http404
            else :
                form = FaqForm(initial = {'timestamp': int(time.time()*1000)})
        else:  # POST

            form = FaqForm(data=request.POST, files=request.FILES)
            if form.data['save'] == 'delete' :
                return delete_item(request, form, kind='Faq')

            if form.is_valid():
                d = form.cleaned_data

                if d['key'] :
                    # updating an existing entry
                    key = ndb.Key('Faq', d['key'])
                    faq = key.get()
                    mem_key = "/faqitem/{0}".format(faq.slug)
                    memcache.delete(mem_key)                # @UndefinedVariable
                else :
                    faq = Faq();

                faq.slug = d.get('slug') or  create_link(d['title'], kind = 'faqs')

                faq.content = d['content']
                faq.title = d['title']
                faq.draft = d['draft']

                faq.timestamp = int(d['timestamp'])
                faq.published_at = datetime.datetime.utcfromtimestamp( int (d['timestamp'])/1000)

                tags = []
                for tag in d['tags'].split(',') :
                    tags.append(tag.strip())
                    update_tag(tag.strip())

                faq.tags = tags

                faq.put()


                if form.data['save'] == 'save_and_continue' :
                    # we need to deal with the eventual consistency problem. So the
                    # page will be first pushed to the cache if we dont' do that we will see
                    # incorrect or missing data

                    memcache.set("/faqitem/{0}".format(faq.slug), faq)  # @UndefinedVariable

                    return HttpResponseRedirect('/edit/%s/?type=faq' % faq.slug)
                else :
                    return HttpResponseRedirect('/list/?type=faq')
            else :
                print form.errors
        return render(request, 'admin/edit-faq.html',{'form': form, 'page': faq} )
    else :
        return HttpResponse("<a href='{}'>login</a>". format(users.create_login_url('/list/')))



def edit_page(request, slug = None):
    '''
    Edits a blog entry or a web page (creates one if needed)
    '''

    if is_authorized_user():
        page = None
        if request.method == 'GET' :
            if slug :
                try :
                    page = memcache.get('/edit/%s/' % slug)  # @UndefinedVariable
                    if not page :
                        key = ndb.Key(urlsafe = slug)
                        page = key.get()

                    p = page.to_dict()

                    p['tags'] = ",".join(p['tags'])
                    p['key'] = page.key.id()
                    if p.get('published_at') :
                        p.pop('published_at')

                    form = PageForm(data = p)
                except:
                    tb = traceback.format_exc()
                    print tb
                    raise Http404
            else :
                form = PageForm(initial = {'timestamp': int(time.time()*1000)})
                form.fields['blog'].initial = True if request.GET.get('type', False) else False;

        else:  # POST
            form = PageForm(data=request.POST, files=request.FILES)
            if form.data['save'] == 'delete' :
                return delete_item(request, form)
            # else

            if form.is_valid():
                d = form.cleaned_data

                if d['key'] :
                    # updating an existing entry
                    key = ndb.Key('Page', d['key'])
                    page = key.get()
                    mem_key = page.get_request_path(d.get('blog'))
                    memcache.delete(mem_key)                # @UndefinedVariable
                    memcache.delete(mem_key +"full")                # @UndefinedVariable
                    memcache.delete(mem_key +"mobile")                # @UndefinedVariable
                else :
                    page = Page();

                if d.get('link') :
                    page.link = d['link']
                else :
                    page.link = create_link(d['title'])

                page.content = d['content']
                page.title = d['title']
                page.draft = d.get('draft', False)
                page.blog = d.get('blog', False)
                page.image = d['image']
                page.timestamp = int(d['timestamp'])
                page.template = d.get('template') or 'blog-post.html'
                page.summary = d['summary'] or re.sub('\s{2,}',' ', strip_tags(d['content']))[0:300]

                page.published_at = datetime.datetime.utcfromtimestamp( int (d['timestamp'])/1000)
                page.priority = d.get('priority',1)

                tags = []
                for tag in d['tags'].split(',') :
                    tags.append(tag.strip())
                    update_tag(tag.strip())

                page.tags = tags
                page.put()

                if page.draft == False and page.blog == True:
                    memcache.set('/',None)  # @UndefinedVariable
                    update_archive(page)

                if request.POST.get('save') == 'save and continue' :
                    # we need to deal with the eventual consistency problem. So the
                    # page will be first pushed to the cache if we dont' do that we will see
                    # incorrect or missing data

                    memcache.set('/edit/%s/' % page.link, page)  # @UndefinedVariable

                    return HttpResponseRedirect('/edit/%s/' % page.link)
                else :
                    if page.blog:
                        return HttpResponseRedirect('/list/?type=blog')
                    else :
                        return HttpResponseRedirect('/list/')
            else :
                print form.errors
        return render(request, 'admin/edit-page.html', {'form': form, 'page': page} )
    else :
        return HttpResponse("<a href='{}'>login</a>". format(users.create_login_url('/list/')))


def create_link(title, recurse = 0, kind = 'page'):
    link = slugify(title)
    try :
        if kind == 'page':
            p = Page.query(Page.link == link).get()
        else :
            p = Faq.query(Faq.slug == link).get()
        if p :
            if recurse == 25 :
                return None
            return create_link(title + str( int(random.random()*1024)) , recurse + 1)
        else :
            return link
    except Exception, e:
        print e
        return None


def delete_item(request, form = None, kind = 'Page'):
    if form :
        if form.data['key'] :
            # updating an existing entry
            if kind == 'Page':
                key = ndb.Key('Page', int(form.data['key']))
                page = key.get()
            else :
                key = ndb.Key('Faq', int(form.data['key']))
                page = key.get()

            return render(request, 'admin/delete.html', {'key': page.key.id, 'title' :page.title , 'kind': kind})
        else :
            return HttpResponse('Sorry but I cant delete non existent pages')
    else :
        key = ndb.Key(request.POST.get('kind','Page'), int(request.POST.get('key')))
        page = key.get()
        key.delete()
        memcache.delete('/edit/%s/' % page.link)  # @UndefinedVariable
        return HttpResponseRedirect('/list/?type=blog')


def item_list(request):
    '''
    Displays the list of pages. We did not bother with pagination in the good old days
    then potato page came in. Now if we get a request that has a page number we send
    only that bit, which also means we use basic template that only contains table
    rows
    '''
    if is_authorized_user():
        t = request.GET.get('type')

        if t == 'blog' :
            pages = Page.query().filter(Page.blog == True).order(-Page.timestamp)
        else :
            if t == 'faq':
                pages = Faq.query().filter()
            else :
                pages = Page.query().filter(Page.blog == False)

        paginator = GaeNdbPaginator(
            pages, 25, batch_size=2)
        pagenum = request.GET.get('page', 1)

        if pagenum == 1:
            template = 'admin/object-list.html'
        else:
            template = 'admin/_objects.html'

        return render(request, template, {'pages': paginator.page(pagenum),
            'obj_type': t, 'pagenum': pagenum}, context_instance = RequestContext(request) )


    else :
        return HttpResponse("<a href='{}'>login</a>". format(users.create_login_url('/list/')))


def error404_finder(request):
    '''
    This is a hack to find 404 by querying each item in the datastore to
    see if it contains a link to a missing page
    '''
    items = [re.compile('serendipity'),
             re.compile('animals-in-concentration-camps.html'), re.compile('example.css')]
    resp = []

    for page in Page.query() :

        for item in items :
            if re.search(item, page.content) :
                resp.append('<a href="/edit/%s">%s</a> for %s ' % (page.link, page.title, item.pattern))

    if resp :
        return HttpResponse(''.join(resp))
    else :
        return HttpResponse('nothing found')


def search_builder(request):
    '''
    Builds a search index
    '''
    if users.is_current_user_admin():
        index = search.Index(name="myIndex")

        # looping because get_range by default returns up to 100 documents at a time
        while True:
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [document.doc_id
                            for document in index.get_range(ids_only=True)]
            if not document_ids:
                break
            # Delete the documents for the given ids from the Index.
            index.delete(document_ids)

        pages = Page.query().filter(Page.draft == False)

        documents = []
        for page in pages :
            if page.blog:
                link = "blog/archives/" + page.link
            else :
                link = page.link

            my_document = search.Document(
                doc_id = str(page.key.id()),
                fields = [search.TextField(name = 'content', value = page.content ) ,
                          search.TextField(name = 'link', value = link),
                          search.TextField(name = 'title', value = page.title.encode('utf-8'))]
            )
            documents.append(my_document)
            if len(documents) == 200:
                documents = []

                print 'saving that lot', index.put(documents), link

        if len(documents) :
            index.put(documents)

        return HttpResponse('Ok')
    else :
        return HttpResponse("<a href='{}'>login</a>". format(users.create_login_url('/rebuild-search/')))



def rebuild_summary(request):
    if is_authorized_user():
        pages = Page.query(Page.blog == True)
        for p in pages:
            if not p.summary :
                content = re.sub(u'</p>',u"</p>\n", p.content)
                p.summary = re.sub(u'\s{2,}',u' ', strip_tags(content))[0:300]
                p.put()

        return HttpResponse('ok')
    else :
        return HttpResponse("<a href='{}'>login</a>". format(users.create_login_url('/rebuild-search/')))
