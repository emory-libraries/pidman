Release 1.0
-----------

* Upgraded to Django 1.8; South migrations have been converted to
  Django migrations.
* SOAP API has been removed.
* Pid noid sequence is now generated with django-sequences and is
  database agnostic (postgres is no longer required).
* Updated to use django-nose as unit test runner.
* Django admin site now customized using a local AdminSite instead of
  extending admin templates.
* Unused usage statistics code has been removed (to be revisited in a
  future version).
* Unused pidman.pidauth has been removed.

Release 0.9.0
-------------
Date: October 2010

New REST API for accessing, creating, and updating Pids and Domains,
with the following features:

* An unathenticated user can GET metadata for an existing PURL or ARK,
  including any qualifiers, via REST.
* An unauthenticated user can GET a list of existing domains via REST.
* An unauthenticated user can GET metadata for a single existing
  domain via REST.
* An authenticated user can create a new ARK, PURL, or qualified ARK
  by POSTing the metadata for the requested ARK or PURL.
* An authenticated user can update an existing ARK, PURL, or qualified
  ARK via REST.
* An authenticated user can create a new Domain or Subdomain by
  POSTing the metadata for the requested Domain.
* An authenticated user can update metadata for an existing Domain.
* An authenticated user can remove an ARK qualifier via HTTP delete.
* When a user attempts to delete an unqualified ARK or PURL, the ARK
  or PURL is not removed and the user gets an error response.
* When a user makes changes to ARKs, PURLs, or Domains via the REST
  API, their actions are tracked just as if the changes were made
  manually through the admin interface.
* A user can search for existing ARKs and PURLs by target, domain,
  etc. via REST.


As of this release, the SOAP API should be considered deprecated.

Deployment Notes
^^^^^^^^^^^^^^^^
* The REST api uses Basic Authentication.  When running under Apache with mod_wsgi,
  add this configuration setting: ``WSGIPassAuthorization On``
* Now requires python module mimeparse.  ``easy_install mimeparse``


Release 0.8.3
-------------
Date: September 2010

* Changed eulcore external to https://svn.library.emory.edu/svn/python-eulcore/trunk/src/eulcore
* Removed south external (This means south will have to be installed on the system.  See README)

Deployment Notes
^^^^^^^^^^^^^^^^
* Make sure externals are updated
* run syncdb
* run migrations

Release 0.8.2
-------------
Date: August 2010

* Bugfix: resolved issue that was causing a general validation error and
  preventing any save or update on an existing pid.
* Users can now delete ARK targets via admin interface.  An ARK with no targets
  is considered inactive.

Release 0.8.1
-------------
Date: March 2010

* Changed banner from "PID Manager" to "Persistent Identifier Manager --
  Emory University Libraries"
* Changed external eulcore to -r 72 .../python-eulcore/trunk/src/eulcore
* Changed LDAP authentication backend to
  eulcore.django.ldap.emory.EmoryLDAPBackend
* Removed dependency on Noid.pm

Deployment Notes
^^^^^^^^^^^^^^^^
* export a copy of the database using pg_dump
* make a copy of the entire persis directory in case we have to put it back quickly
* svn revert any modified files
* Switch to the correct tag or branch:
    * Staging: svn switch to branches/release_0.8.x and update
    * Production: svn switch to tags/release_0.8.1 and update
* from within the pidman directory run::
    $ python ./manage.py syncdb
    $ python ./manage.py migrate
* Restart apache

Release 0.7.0
-------------
Date: October 6, 2009
SVN revision: 274

Comment: The solution to fix the broken migration is done in this deployment.
Migrations are removed and then replaced with newly created migrations.

Deployment Notes
^^^^^^^^^^^^^^^^
*Part One:*

Make sure you are using django South version 0.6.1.
The production version of South (0.6.0) does not handle
constraints correctly.

*Part Two (DIRAC - terminal window):*

Export entire database and schema for backup purposes only::

    $ dirac> cd /home/persis
    $ dirac> pg_dump persis | gzip > dirac_persis_all.gz
    $ dirac> pg_dump -a persis -f dirac_persis_data_only.sql
    $ dirac> pg_dump -s persis -f dirac_persis_schema_only.sql

Export needed data from production/dirac::

    $ dirac> pg_dump -a -D -O -t pid_pid persis > table_pid_pid.sql
    $ dirac> pg_dump -a -D -O -t pid_target persis > table_pid_target.sql
    $ dirac> pg_dump -a -D -O -t pid_proxy persis > table_pid_proxy.sql
    $ dirac> pg_dump -a -D -O -t pidauth_domain persis > table_pid_domain.sql
    $ dirac> pg_dump -a -D -O -t pid_extsystem persis > table_pid_extsystem.sql
    $ dirac> pg_dump -a -D -O -t auth_user persis > table_auth_user.sql

copy these output sql files to wilson. ie. One way to do this:

* on ubuntu Places->Connect to Server popup
* set Service type: SSH
* Server: dirac
* etc.
* Repeat for wilson, and copy using file manager gui

*Part Three (WILSON - phpPgAdmin GUI) DATABASE SETUP:*

phpPgAdmin gui tool> drop the database persis
phpPgAdmin gui tool> create a new database persis
(Be sure to set encoding to "UTF8".)

Part Four (WILSON - terminal window) TABLE SETUP::
    $ wilson> cd /home/persis
    $ wilson> run python manage.py syncdb.
    $ wilson> python manage.py migrate.

Verify that all the table constraints are correct.

Part Five (WILSON - terminal window): IMPORT TABLE DATA

Adjust data sql dump files for tables (if needed).

Load sql files on new database::

    $ wilson> psql dbname username < table_auth_user.sql
    $ wilson> psql dbname username < table_pid_extsystem.sql

Adjust pidauth_domain, search and replace pidauth with pid::

    $ wilson> psql dbname username < table_pid_domain.sql
    $ wilson> psql dbname username < table_pid_proxy.sql
    $ wilson> grep "false, " table_pid_pid.sql > table_fix_active_flag_in_pid_target.sql

Adjust table to look like this::
    $ update pid_target
    $ set active - 'false'
    $ from pid_pid
    $ where pid_target.pid_id - pid_pid.id and pid_pid.pid - '2wsmq';

Adjust table_pid_pid.sql - remove active column and data
    * search/replace 'true, '
    * search/replace 'false, '
    * search/replace 'active, '
    * wilson> psql dbname username < table_pid_pid.sql
    * wlson> psql dbname username < table_pid_target.sql
    * wilson> psql dbname username < table_fix_active_flag_in_pid_target.sql