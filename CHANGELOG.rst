Release 1.0.3
-------------

* Fix admin base template so site header and title are included.
* Add configurable admin site title suffix to help differentiate instances
  of the pid manager.
* bugfix: REST API search previously did not return pids in subdomains
  when searching by domain.

Release 1.0.2
-------------

* Disable linkcheck display in pid admin change list

Release 1.0.1
-------------

* Clean up merge errors (duplicated imports, etc)
* Require django-linkcheck 1.2, since 1.3 causes issues with test fixture data

Release 1.0
-----------

* Domain/collection hierarchy now handled with
  `django-mptt <http://django-mptt.github.io/django-mptt/>`_.
* Now using `django-eultheme <https://github.com/emory-libraries/django-eultheme>`_
  for error pages and for `django-downtime <https://github.com/dstegelman/django-downtime>`_
  integration.
* Admin search field list for pids has been customized in an effort
  to address slow search response.
* Documentation has been overhauled and updated, including providing
  REST API examples for multiple programming languages.
* Updated and refined
  `django-linkcheck <https://github.com/DjangoAdminHackers/django-linkcheck>`_


Release 0.10
------------
June 2016

.. NOTE::

  This is an interim release intended for migrating data.  You should
  upgrade to the 1.0 release once the database migration is complete.

* **SOAP API has been removed.**
* Upgraded to Django 1.8; South migrations have been converted to
  Django migrations.
* Pid noid sequence is now generated with django-sequences and is
  database agnostic (postgres is no longer required).
* Pid target uri is now a URLField instead of a CharField.
* Updated to use `django-nose <https://django-nose.readthedocs.org/en/latest/>`_
  as unit test runner.
* New migration script to migrate data from an old database
  to a new one (i.e., postgres to mysql).
* Django admin site now customized using a local AdminSite instead of
  extending admin templates.
* Unused usage statistics code has been removed (to be revisited in a
  future version).
* Unused pidman.pidauth has been removed.
* InvalidArk proxy model has been removed (application no longer allows
  invalid arks to be created).
* Now using `django-admin-bootstrapped <https://github.com/django-admin-bootstrapped/django-admin-bootstrapped>`_
  for admin templates.
* Now using `django-auth-ldap <https://pythonhosted.org/django-auth-ldap/>`
  for LDAP login instead of eullocal.
* Enabled `django-logentry-admin <https://github.com/yprez/django-logentry-admin>`_
  to provide minimal view access to admin log entries.
* Legacy documentation that is no longer relevant has been removed.

Release 0.9.0
-------------
October 2010

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


Release 0.8.3
-------------
September 2010

* Updated eulcore version and south installation process.

Release 0.8.2
-------------
August 2010

* Bugfix: resolved issue that was causing a general validation error and
  preventing any save or update on an existing pid.
* Users can now delete ARK targets via admin interface.  An ARK with no targets
  is considered inactive.

Release 0.8.1
-------------
March 2010

* Changed admin banner from "PID Manager" to "Persistent Identifier Manager --
  Emory University Libraries"
* Updated to a newer version of eulcore
* Changed LDAP authentication backend to
  eulcore.django.ldap.emory.EmoryLDAPBackend
* Removed dependency on Noid.pm


Release 0.7.0
-------------
October 2009

* Fixed broken db migrations.
