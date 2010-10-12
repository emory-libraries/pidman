# This is a sample localsettings.py. Copy it to localsettings.py and fill it
# with settings relevant to your local server.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# LDAP login settings. These are configured for emory, but you'll need
# to get a base user DN and password elsewhere.
AUTH_LDAP_SERVER = 'ldaps://vlad.service.emory.edu'
AUTH_LDAP_BASE_USER = ''           # DN of the base LDAP user (e.g., 'uid=foo,ou=bar,o=emory.edu')
AUTH_LDAP_BASE_PASS = ''           # password for that user
AUTH_LDAP_SEARCH_SUFFIX = 'o=emory.edu'
AUTH_LDAP_SEARCH_FILTER = '(uid=%s)'
AUTH_LDAP_CHECK_SERVER_CERT = True # set to False to skip server cert verification (TESTING ONLY)
AUTH_LDAP_CA_CERT_PATH = ''        # full path to CA cert bundle

# This should be private and unique per server. In a pinch, something from
# `uuidgen` should do.
SECRET_KEY = ''

# This should be the path to the noid db, used by the mint_noid stored
# procedure to generate noids.
NOID_DB_PATH = '/tmp/noid'

# Information needed for generating new ARKs and PURLs:
#  - base url for all pids (where the pid resolver is installed)
#  - name authority number for ARKs
PID_RESOLVER_URL = 'http://pidtest.library.emory.edu'
PID_ARK_NAAN = '25593'

# If you're running under apache, this will need to be the absolute path of
# any templates directories. If you're just running with manage.py (e.g., in
# dev/testing), then it can be relative paths. 
TEMPLATE_DIRS = (
    'templates',
)

EXTENSION_DIRS = (
    # This works for manage.py, but running under apache requires an
    # absolute path.

    # '../external/django-modules',
)

