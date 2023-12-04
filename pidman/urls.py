"""pidman URL Configuration"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from pidman.admin import admin_site


urlpatterns = [
    # pidman has no user-facing index, so redirect from base site url
    # to site admin page

    url(r'^$', RedirectView.as_view(url='admin/', permanent=False),
        name="site-index"),
    url(r'^admin/linkcheck/', include(('linkcheck.urls', 'linkcheck'), namespace='linkcheck')),
    url(r'^admin/', admin_site.urls),

    # REST API urls live under top-level, but should not conflict with resolver urls
    url(r'^', include(('pidman.rest_api.urls', 'rest_api'), namespace='rest_api')),
    # let everything else fall through to the resolver
    url(r'^', include(('pidman.resolver.urls', 'resolver'), namespace='resolver')),
]
