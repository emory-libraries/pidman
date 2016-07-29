Overview
--------

.. image:: https://travis-ci.org/emory-libraries/pidman.svg
    :alt: Travis-CI build status
    :target: https://travis-ci.org/emory-libraries/pidman

.. image:: https://coveralls.io/repos/github/emory-libraries/pidman/badge.svg
    :target: https://coveralls.io/github/emory-libraries/pidman?branch=develop
    :alt: Code Coverage

.. image:: https://codeclimate.com/github/emory-libraries/pidman/badges/gpa.svg
   :target: https://codeclimate.com/github/emory-libraries/pidman
   :alt: Code Climate

.. image:: https://requires.io/github/emory-libraries/pidman/requirements.svg
   :target: https://requires.io/github/emory-libraries/pidman/requirements/
   :alt: Requirements Status
   
.. image:: https://landscape.io/github/emory-libraries/pidman/master/landscape.svg?style=flat
   :target: https://landscape.io/github/emory-libraries/pidman/master
   :alt: Code Health

**pidman** is a Django application for maintaining, managing, and
resolving PURLs (Permanent URLs) and ARKs (Archival Resource Keys).
Together these resources allow the assignment of unique persistent
identifiers.

You can find more information on `ARKs
<http://en.wikipedia.org/wiki/Archival_Resource_Key>`_ and `PURLs
<http://purl.oclc.org/docs/index.html>`_ or view the complete `ARK
specification
<https://confluence.ucop.edu/download/attachments/16744455/arkspec.txt?version=1>`_

License
-------

This software is distributed under the Apache 2.0 License.

Components
----------

The component applications of this project are:

:mod:`~pidman.pid`
^^^^^^^^^^^^^^^^^^

Core application to represent pid objects and build central behaviors
for them.  All (non-scripted) management and editing is handled
through the Django Admin interface.

:mod:`~pidman.resolver`
^^^^^^^^^^^^^^^^^^^^^^^

Public-facing resolver that redirects ARK and PURLs URLs to their
Target URLs; also provides


:mod:`~pidman.rest_api`
^^^^^^^^^^^^^^^^^^^^^^^

Provides a REST API for selected pid functions such as create, edit
and delete model objects from :mod:`pidman.pid.models`.

