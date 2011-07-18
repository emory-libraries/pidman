# Django settings for pidman project.
from os import path

# Get the directory of this file for relative dir paths.
# Django sets too many absolute paths.
BASE_DIR = path.dirname(path.abspath(__file__))

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'pidman.urls'

TEMPLATE_DIRS = (
    path.join(BASE_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',  
#    'django.contrib.history',

    #'eulcore', # https://svn.library.emory.edu/svn/django-eulcore/
    'eulcore.django.emory_ldap',
    'south', # http://south.aeracode.org/
    'linkcheck', #http://code.google.com/p/django-linkcheck/

    'pidman.soap_api',    
    'pidman.pid',
    'pidman.pidauth',
    'pidman.resolver',
    'pidman.usage_stats',
    'pidman.rest_api',
)

AUTH_PROFILE_MODULE = 'emory_ldap.EmoryLDAPUserProfile'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'eulcore.django.emory_ldap.backends.EmoryLDAPBackend'
    #'pidman.ldapext.PidmanLDAPBackend',
    #'eulcore.ldap.auth.backends.LDAPBackend'
)

# SOUTH MIGRATIONS SETTINGS
# See various setting documentations under http://south.aeracode.org/wiki/Documentation
SKIP_SOUTH_TESTS = True # Disable south app tests.py, they shouldn't run during mine.
# SOUTH_TESTS_MIGRATE = True # If migrations are needed to run fixtures.
# SOUTH_AUTO_FREEZE_APP = False # Related to freezing apps during migrations.

# if this token is in target URI it will be replaced with the noid after it is minted
PID_REPLACEMENT_TOKEN = "{%PID%}"

# Usage Log Settings
USAGE_LOG_EXCLUDE_IPS = [
    '170.140.223.57', #nagios server
    '170.140.140.11', #gsa-crawler
    '170.140.140.12', #gsa-crawler
]
USAGE_LOG_EXCLUDE_REQUEST_PATTERNS = [
    '^GET /resolver/resolver/handler.*',
    '^GET /robots\.txt.*',
]

USAGE_LOG_EXCLUDE_AGENTS_PATTERNS = [
    '.*Googlebot.*',
    '.*Ask Jeeves.*',
    '.*msnbot.*',
]
try:
    from localsettings import *
except ImportError:
    import sys
    print >>sys.stderr, 'No local settings. Trying to start, but if ' + \
        'stuff blows up, try copying localsettings-sample.py to ' + \
        'localsettings.py and setting appropriately for your environment.'
    pass

try:
    # use xmlrunner if it's installed; default runner otherwise. download
    # it from http://github.com/danielfm/unittest-xml-reporting/ to output
    # test results in JUnit-compatible XML.
    import xmlrunner
    TEST_RUNNER='xmlrunner.extra.djangotestrunner.XMLTestRunner'
    TEST_OUTPUT_DIR='test-results'
    TEST_OUTPUT_VERBOSE = True
    TEST_OUTPUT_DESCRIPTIONS = True
except ImportError:
    pass

EXTENSION_DIRS = (
    path.join(BASE_DIR, '../external/django-modules'),
)

import sys
try:
    sys.path.extend(EXTENSION_DIRS)
except NameError:
    pass # EXTENSION_DIRS not defined. This is OK; we just won't use it.
del sys
