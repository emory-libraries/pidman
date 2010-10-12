from django.conf.urls.defaults import *
from django.contrib import admin
from pidman.linkcheck_config import linklists #This needs some kind of autodiscovery mechanism

admin.autodiscover()

urlpatterns = patterns('',
#    (r'^admin/access_log/', include('pidman.usage_stats.urls')),
    (r'^$', 'pidman.views.redirect_to',
        {'url': 'admin/', 'permanent': False}),
#    (r'^admin/linkcheck/', include('linkcheck.urls')), # linkcheck admin
    (r'^admin/', include(admin.site.urls)),
    # soap api for backwards compatibility with legacy rails app
    (r'^persis_api/', include('pidman.soap_api.urls')),   

    # let everything else fall through to the resolver
    (r'^', include('pidman.resolver.urls')),
)
