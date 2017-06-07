from django.conf.urls import patterns,  url

urlpatterns = patterns('',
    url(r'^(?P<slug>.*)/$', "faqs.views.catch_all"),
)