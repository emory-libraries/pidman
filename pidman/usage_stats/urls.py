from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'(?P<year>\d{4})?', 'usage_stats.views.export'),
)
