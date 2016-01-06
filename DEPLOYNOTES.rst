.. _DEPLOYNOTES:

DEPLOYNOTES
===========

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

After configuring your database, run syncdb::

    python pidman/manage.py syncdb
    python pidman/manage.py migrate

To verify installation execute without errors::

    python pidman/manage.py test

.. NOTE::

    Deploying to QA and Production should be done using ``fab deploy``.

.. NOTE::

    When running under Apache and mod_wsgi, configure
    ``WSGIPassAuthorization On`` (this is required for Basic
    Authentication in the REST API).

