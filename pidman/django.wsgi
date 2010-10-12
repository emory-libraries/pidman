import os
import sys
import django.core.handlers.wsgi

# path is the parent directory of this script
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if path not in sys.path:
    sys.path.append(path)

sys.path.append(path + '/external/django-modules')
sys.path.append(path + '/pidman')

os.environ['DJANGO_SETTINGS_MODULE'] = 'pidman.settings'

application = django.core.handlers.wsgi.WSGIHandler()
