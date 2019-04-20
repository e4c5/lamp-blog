from django.conf.urls import url
from legacy import legacy_importer 
from django.views.generic.base import RedirectView

from pages import admin_views, views, home
from pages.admin_views import edit_page, delete_item, item_list, search_builder,\
    error404_finder
from photos.views import upload_handler
from contact import views as contact_views

# This section is for page editing
urlpatterns = [
    url(r'^edit/(?P<slug>.*(php|html))$', edit_page),
    url(r'^edit/(?P<slug>.*)/$', edit_page),
    url(r'^edit/$', edit_page),
    url(r'^delete/$', delete_item),
    url(r'^list/$', item_list),
    url(r'^upload/$', upload_handler),    
]

# the following section is usefull only during development and should be
# commented out after deployment is completed.
urlpatterns += [
    url(r'^importer/$', legacy_importer),
    url(r'^rebuild-tags/$', admin_views.rebuild_tags),
    url(r'^rebuild-arch/$', admin_views.rebuild_sidebar),
    url(r'^rebuild-search/$', search_builder),
    url(r'^find-404/$', error404_finder),
 ]

# this section is for the blog

urlpatterns += [
    url(r'^blog/tag/$', views.tags),
    url(r'^blog/tag/(?P<slug>[A-Za-z0-9_-]+)/$', views.posts_tagged),

    url(r'^blog/feed/$', views.rss), # fixem
    url(r'^feed/$', views.rss), # fixmme

    url(r'^blog/archives/$', views.archives),
    url(r'^blog/$', home.blog_main),
    url(r'^blog/page/(?P<page>[0-9]{1,3})/$', home.blog_main),

    # some redirects to keep things neat and tidy
    #
    url(r'^archives/index.php$', RedirectView.as_view(url='/blog/archives/')),
    url(r'^blog/archives/0{1,3}(?P<qq>[0-9]{2,4}.html)$', RedirectView.as_view(url="/blog/archives/%(qq)s")),


    url(r'^blog/(?P<year>[0-9]{4})/$', views.archives),
    url(r'^blog/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.archives),
    
    # next one is for a bunch of incorrectly set legacy permalinks
    url(r'^blog/[0-9]{4}/[0-9]{2}/[0-9]{2}/(?P<slug>[A-Za-z0-9_-]+)/$', RedirectView.as_view(url="/blog/archives/%(slug)s.html")),
    url(r'^blog/archives/(?P<slug>[A-Za-z0-9_-]+\.{0,4}html)$', views.blog_catch_all),
]

# next section is for pages and topics
urlpatterns += [
    url(r'^$', home.home),
    url(r'^contact/$', RedirectView.as_view(url='/contact.php')),
    url(r'^contact.php', contact_views.contact),
    url(r'^(?P<slug>.*)/$', views.catch_all),
    url(r'^(?P<slug>.*(php|html))$', views.catch_all),
]

