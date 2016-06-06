from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<noid>[a-z0-9]+)$', views.resolve_purl),
    # either / or . can delimit the end of ark name and the beginning of the qualifier
    url(r'^ark:/(?P<naan>\d+)/(?P<noid>[a-z0-9-]+)[/.]?(?P<qual>[a-zA-Z0-9=#*+@_$%-./]*)',
        views.resolve_ark),
]
