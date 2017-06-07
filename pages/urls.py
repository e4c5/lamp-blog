from django.conf.urls import patterns,  url, include
from pages.admin_views import edit_page, delete_item, item_list, search_builder,\
    error404_finder
from legacy import legacy_importer 
from django.views.generic.base import RedirectView

# This section is for page editing
urlpatterns = patterns('',
    url(r'^edit/(?P<slug>.*(php|html))$', edit_page),
    url(r'^edit/(?P<slug>.*)/$', edit_page),
    url(r'^edit/$', edit_page),
    url(r'^delete/$', delete_item),
    url(r'^list/$', item_list),
    url(r'^upload/$','photos.views.upload_handler'),    
)

# the following section is usefull only during development and should be
# commented out after deployment is completed.
# urlpatterns += patterns('',
#    url(r'^importer/$', legacy_importer),
#    url(r'^rebuild-tags/$', 'pages.admin_views.rebuild_tags'),
#    url(r'^rebuild-arch/$', 'pages.admin_views.rebuild_sidebar'),
#    url(r'^rebuild-search/$', search_builder),
#    url(r'^find-404/$', error404_finder),
                        
#)

# this section is for the blog

urlpatterns += patterns('',
    url(r'^blog/tag/$', 'pages.views.tags'),
    url(r'^blog/tag/(?P<slug>[A-Za-z0-9_-]+)/$', 'pages.views.posts_tagged'),

    url(r'^blog/feed/$', 'pages.views.rss'), # fixem
    url(r'^feed/$', 'pages.views.rss'), # fixmme

    url(r'^blog/archives/$', 'pages.views.archives'),
    url(r'^blog/$','pages.home.blog_main'),
    url(r'^blog/page/(?P<page>[0-9]{1,3})/$','pages.home.blog_main'),

    # some redirects to keep things neat and tidy
    #
    url(r'^archives/index.php$', RedirectView.as_view(url='/blog/archives/')),
    url(r'^blog/archives/0{1,3}(?P<qq>[0-9]{2,4}.html)$', RedirectView.as_view(url="/blog/archives/%(qq)s")),


    url(r'^blog/(?P<year>[0-9]{4})/$', 'pages.views.archives'),
    url(r'^blog/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', 'pages.views.archives'),
    
    # next one is for a bunch of incorrectly set legacy permalinks
    url(r'^blog/[0-9]{4}/[0-9]{2}/[0-9]{2}/(?P<slug>[A-Za-z0-9_-]+)/$', RedirectView.as_view(url="/blog/archives/%(slug)s.html")),
    url(r'^blog/archives/(?P<slug>[A-Za-z0-9_-]+\.{0,4}html)$', 'pages.views.blog_catch_all'),

    
)

# next section is for pages and topics
urlpatterns += patterns('',
    url(r'^$', 'pages.home.home'),
    url(r'^contact/$', RedirectView.as_view(url='/contact.php')),
    url(r'^contact.php','contact.views.contact'),
    url(r'^(?P<slug>.*)/$', 'pages.views.catch_all'),
    url(r'^(?P<slug>.*(php|html))$', 'pages.views.catch_all'),
)

