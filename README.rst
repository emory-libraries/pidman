Overview
--------

This is a management application for maintaining, managing, and
resolving PURLs (Permanent URLs) and ARKs (Archival Resource Keys).
Together these resources allow the assignment of unique persistent
identifiers.

You can find more information on `ARKs
<http://en.wikipedia.org/wiki/Archival_Resource_Key>`_ and `PURLs
<http://purl.oclc.org/docs/index.html>`_ or view the complete `ARK
specification
<https://confluence.ucop.edu/download/attachments/16744455/arkspec.txt?version=1>`_


Dependencies
------------

 * soaplib==0.8.1 -  http://pypi.python.org/pypi/soaplib
 * psycopg2    - currently requires postgres & psycopg2 for stored procedure
 * python-ldap
 * python-lxml - http://codespeak.net/lxml/installation.html
 * django 1.2+
 * south==0.7.2

Components
----------

The component applications of this project are:

:mod:`~pidman.pid`
^^^^^^^^^^^^^^^^^^

Core application to represent pid objects and build central behaviors
for them.  All (non-scripted) management and editing is handled
through the Django Admin interface.

:mod:`~pidman.pidauth`
^^^^^^^^^^^^^^^^^^^^^^

Unused: initially to allow for intended for per-domain permissions,
but not implemented.

:mod:`~pidman.resolver`
^^^^^^^^^^^^^^^^^^^^^^^

Public-facing resolver that redirects ARK and PURLs URLs to their
Target URLs; also provides


:mod:`~pidman.rest_api`
^^^^^^^^^^^^^^^^^^^^^^^

Provides a REST API for selected pid functions such as create, edit
and delete model objects from :mod:`pidman.pid.models`.

:mod:`~pidman.soap_api`
^^^^^^^^^^^^^^^^^^^^^^^

Provides a limited SOAP API for creating ARKs and PURLs and updating
ARK and PURL target URIs.  Designed to be backwards-compatible (as
much as possible) with the SOAP API of the previous, Rails-based,
incarnation of this PID Manager application. **Deprecated**; new
projects should use the REST API instead.
