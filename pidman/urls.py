"""pidman URL Configuration"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    # pidman has no user-facing index, so redirect from base site url
    # to site admin page
    url(r'^$', RedirectView.as_view(url='admin/', permanent=False)),
    url(r'^admin/', include(admin.site.urls)),

    # REST API urls live under top-level, but should not conflict with resolver urls
    url(r'^', include('pidman.rest_api.urls', namespace='rest_api')),
    # let everything else fall through to the resolver
    url(r'^', include('pidman.resolver.urls')),
]
