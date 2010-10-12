Dependencies
============

soaplib -  http://pypi.python.org/pypi/soaplib
psycopg2 - currently requires postgres & psycopg2 for stored procedure
noid - see below for setup instructions


Extensions
==========
We rely on a couple of externally-developed extensions. They need to be
downloaded added to the python path. Extensions are listed in settings.py
and annotated with where they can be downloaded. Put them into a directory
and add that local path to the EXTENSION_DIRS in localsettings.py.


noid setup
==========
# minimal directions to make a grossly insecure noid db (FIXME: automate!)
$ noid -f /tmp/noid dbcreate .zek
$ chmod -R go+rw /tmp/noid # for postgres
$ noid -f /tmp/noid mint 1
