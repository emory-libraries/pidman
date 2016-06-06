from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<type>(purl|ark))/$', views.create_pid, name='create-pid'),
    url(r'^(?P<type>(purl|ark))/(?P<noid>[a-z0-9]+)$', views.pid, name='pid'),
    # PURLs can only have a single target, with no qualifier
    url(r'^purl/(?P<noid>[a-z0-9]+)/$', views.target,
            {'type': 'purl', 'qualifier': ''}, name='purl-target'),
    # ARKs can have multiple targets
    url(r'^ark/(?P<noid>[a-z0-9]+)/(?P<qualifier>[a-zA-Z0-9=#*+@_$%-./]*)$',
            views.target, {'type': 'ark'}, name='ark-target'),
    url(r'^domains/$', views.domains, name='domains'),
    url(r'^domains/(?P<id>\d+)/$', views.domain, name='domain'),
    url(r'^pids/$', views.search_pids, name="search-pids"),
]
