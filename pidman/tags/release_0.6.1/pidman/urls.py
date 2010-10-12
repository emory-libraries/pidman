from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'pidman.views.redirect_to',
        {'url': 'admin/', 'permanent': False}),
    (r'^admin/(.*)', admin.site.root),

    # soap api for backwards compatibility with legacy rails app
    (r'^persis_api/', include('pidman.soap_api.urls')),   
)
