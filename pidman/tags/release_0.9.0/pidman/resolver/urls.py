from django.conf.urls.defaults import *

urlpatterns = patterns('pidman.resolver.views',
    (r'^(?P<noid>[a-z0-9]+)$', 'resolve_purl'),
    # either / or . can delimit the end of ark name and the beginning of the qualifier
    (r'^ark:/(?P<naan>\d+)/(?P<noid>[a-z0-9-]+)[/.]?(?P<qual>[a-zA-Z0-9=#*+@_$%-./]*)', 'resolve_ark'),
)
