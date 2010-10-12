import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'pidman.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

sys.path.append('/usr/local/lib/python2.6/site-packages/django')
sys.path.append('/home/persis/manager')
