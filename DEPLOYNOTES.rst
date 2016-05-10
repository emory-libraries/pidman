.. _DEPLOYNOTES:

Deploy Notes
============

Installation
------------

Instructions to install required software and systems, configure the application,
and run various scripts to load initial data.

Software Dependencies
~~~~~~~~~~~~~~~~~~~~~

You should use `pip <http://pip.openplans.org/>`_ and `virtualenv
<http://virtualenv.openplans.org/>`_ for environment and dependency
management in this and other Python projects. If you don't have them
installed, you can get them with ``sudo easy_install pip`` and then
``sudo pip install virtualenv``.

------

Bootstrapping a development environment
---------------------------------------

* Copy ``pidman/localsettings.py.sample`` to ``pidman/localsettings.py``
  and configure local settings, including: **DATABASES**,  **SECRET_KEY**,
  **LDAP**, **PID_RESOLVER_URL**, **PID_ARK_NAAN**, and **LOGGING**.
* Create a new virtualenv and activate it.
* Install fabric: ``pip install fabric``
* Use fabric to run a local build, which will install python dependencies in
  your virtualenv, run unit tests, and build sphinx documentation: ``fab build``

After configuring your database, run migrate::

    python manage.py migrate

To verify installation execute without errors::

    python manage.py test

.. NOTE::

    Deploying to QA and Production should be done using ``fab deploy``.

.. NOTE::

    When running under Apache and mod_wsgi, configure
    ``WSGIPassAuthorization On`` (this is required for Basic
    Authentication in the REST API).


Upgrade Notes
-------------

1.0
~~~

* This update includes `django-downtime <https://github.com/dstegelman/django-downtime>`_
  for maintenance mode.  You may want to customize **DOWNTIME_EXEMPT_PATHS**
  and **DOWNTIME_ALLOWED_IPS**.  Downtime can be scheduled via
  the web admin or started manually using the ``downtime_start`` and
  ``downtime_end`` manage commands.

* Configure a linkcheck **SITE_DOMAIN** in ``localsettings.py`` and
  schedule a cron job to run the linkcheck manage command to enable
  periodic link checking on Pid targets::

      python manage.py checklinks --limit [maximum number of links to check]

  By default, linkcheck will recheck urls once a week, but that can be
  configured in ``localsettings.py``.  See the
  `django-linkcheck settings documentation <https://github.com/DjangoAdminHackers/django-linkcheck#settings>`_ for details.


0.10
~~~~

* This release includes an update from Django 1.2 to Django 1.8, so some
  files have been moved or renamed.  You should update any Apache
  configuration files or cron jobs that reference these.

  * ``manage.py`` is now at the top level instead of at ``pidman/manage.py``
  * WSGI script is now at ``pidman/wsgi.py``

* Static files such as CSS and Javascript are now handled by Django
  staticfiles.  Apache configuration should be updated to alias
  ``static/`` to the static directory created by the deploy ``pidman/static``.

* LDAP login is now handled by
  `django-auth-ldap <https://pythonhosted.org/django-auth-ldap/>`_.  LDAP
  configuration settings should be updated in ``localsettings.py``;
  see the example configuration in ``localsettings.py.sample``.

* After configurations are updated, run database migrations.  For a
  new installation, use ``python manage.py migrate``.

  *If you are upgrading an existing instance*, you will need to fake
  initial migrations for several models.  This sequence should work::

    # fake content type initial migration (dependency for several other models)
    $ python manage.py migrate contenttypes --fake-initial
    # run migrations for new apps
    $ python manage.py migrate sequences linkcheck
    # migrate all other existing models, faking initial migrations
    $ python manage.py migrate --fake-initial

* *OPTIONAL*: if you want to configure the previous pidman instance to
  run in read-only mode during the data migration to prevent new pids from
  being created, you should configure django to access the database using
  a database user with only the following permissions on the database:

  - **SELECT** on the entire database
  - **INSERT**, **UPDATE**, **DELETE** on ``django_session``
  - **UPDATE** ``last_login`` on ``auth_user``

  This will allow users to log in to the admin site, but will throw a
  500 error if anyone tries to create or modify data via the admin site
  or via the REST API.

* To migrate data from an existing database (i.e postgres to mysql), you
  should configure a second database named **postgres** in ``localsettings.py``
  (see example configuration in ``localsettings.py.sample``), and then
  run ``python manage.py pg-migrate``.  Where there is existing content
  (e.g., for content types), the script will prompt you to remove content
  before copying data; this is required in order to ensure
  primary ids are propagated correctly in the migration.

  The script includes options to summarize object counts in both databases
  and to sync content by chunks.  Run with ``-h`` for specifics.

  .. Note::

    Make sure that the character encoding for the two databases matches
    to avoid encoding issues.  UTF-8 is recommended.

0.9
~~~

* The REST api uses Basic Authentication.  When running under Apache
  with mod_wsgi, use this configuration setting: ``WSGIPassAuthorization On``


