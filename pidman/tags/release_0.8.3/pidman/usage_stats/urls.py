from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'(?P<year>\d{4})?', 'pidman.usage_stats.views.export'),
)
