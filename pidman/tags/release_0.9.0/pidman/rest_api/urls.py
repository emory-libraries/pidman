from django.conf.urls.defaults import *

urlpatterns = patterns('pidman.rest_api.views',
    url(r'^(?P<type>(purl|ark))/$', 'create_pid', name='create-pid'),
    url(r'^(?P<type>(purl|ark))/(?P<noid>[a-z0-9]+)$', 'pid', name='pid'),
    # PURLs can only have a single target, with no qualifier
    url(r'^purl/(?P<noid>[a-z0-9]+)/$', 'target',
            {'type': 'purl', 'qualifier': ''}, name='purl-target'),
    # ARKs can have multiple targets 
    url(r'^ark/(?P<noid>[a-z0-9]+)/(?P<qualifier>[a-zA-Z0-9=#*+@_$%-./]*)$',
            'target', {'type': 'ark'}, name='ark-target'),
    url(r'^domains/$', 'domains', name='domains'),
    url(r'^domains/(?P<id>\d+)/$', 'domain', name='domain'),
    url(r'^pids/$', 'search_pids', name="search-pids"),
)
