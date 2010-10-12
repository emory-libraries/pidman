from django.conf.urls.defaults import *

urlpatterns = patterns('pidman.soap_api.views',
    # everything goes through the pid_service
    (r'', 'pid_service'),
)
