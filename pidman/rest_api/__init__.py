'''
The pid manager REST API provides access for Create, Read, Update, and
limited Delete on :class:`~pidman.pid.models.Pid`,
:class:`~pidman.pid.models.Domain`, and
:class:`~pidman.pid.models.Target` objects.

Create and update methods require Basic Authentication with a user
who has permission to take those actions.  Create methods generally
use POST with form data; update methods generally use PUT with JSON
data.  Results return JSON data or a URI value.

Currently, the *only* supported format is JSON.

* Domains:

 - **/domains/**

   + use GET to list information about all domains
   + use POST to create a new domain (see
     :meth:`~pidman.rest_api.views.domains` for a list of
     supported and required parameters)

 - **/domains/#/** (where # is an domain id number)

   + use GET to retrieve a single domain by id number
   + PUT data in json format to update an existing domain - see
     :meth:`~pidman.rest_api.views.domain`

* Pids and Targets:

 - **/ark/** or **/purl/** - POST to create a new ark or purl; see
   :meth:`~pidman.rest_api.views.create_pid`
 - **/ark/8g3sq** or **/purl/127zr** - pid by type and noid

   + GET to retrieve information about an existing ARK or PURL and
     associated targets
   + PUT data in json to update pid info - see
     :meth:`~pidman.rest_api.views.pid`

 - **/purl/127zr/** or **/ark/8g3sq/** or **/ark/8g3sq/qualifier**

   + GET to retrieve information about a single target by qualifier;
     use trailing slash after the pid for unqualified target (only
     target for a PURL)
   + PUT to update an existing target OR create a new ARK target, see
     :meth:`~pidman.rest_api.views.target`
   + DELETE to remove a target (ARK only)

 - **/pids/?** - search pids; see :meth:`~pidman.rest_api.views.search_pids`
   for supported search terms


NOTE:  The or term **uri** is used throughout, and occurs as a key in several
JSON returns to refer to the REST API location of the Domain, Pid, or Target
object as a resource, which is distinct from the the **access_uri** (the address
where a Purl, Ark, or Qualified Ark should be requested in order to resolve to
the contents of that Purl or Ark) and the **target_uri** (the uri that a Purl or
Ark will resolve to when requested via the access_uri).

------------------------
'''
