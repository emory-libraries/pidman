import json
from urlparse import urlparse

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse, resolve
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden

from eulcore.django.http import HttpResponseUnauthorized

from pidman.pid.models import Pid, Target, Domain, ExtSystem, Proxy, Policy
from pidman.pid.ark_utils import valid_qualifier
from pidman.rest_api.decorators import basic_authentication

json_serializer = DjangoJSONEncoder(ensure_ascii=False, indent=2)

BASIC_AUTH_REALM = 'PID Manager'
# NOTE: Basic Auth when deployed with Apache & mod_wsgi may require this setting:
# WSGIPassAuthorization On

class BadRequest(Exception):
    # Custom exception to simplify error-handling with REST views
    pass

def _log_rest_action(request, object, action, msg):
    """
    This adds actions to the standard django admin LogEntry model as if it were
    performed via the admin interface.  Simple place the log entry after the 
    action for create or update functions or *before* the action in if deleting
    an object.

    Example of use for creating a new object::

        obj = Object(**params)
        obj.save()
        _log_rest_action(request, obj, ADDITION, "Created Object %s" % obj.__unicode__)

    Example of use for deleting an object::

        obj = Object.objects.get(pk=1)
        _log_rest_action(request, obj, DELETION, "Deleted Object %s" % obj.__unicode__)
        obj.delete()

    :param request: request generating the action.
    :param object: object being modified.
    :param action: static variable for action from `django.admin.model`
                   limited to ADDITION, CHANGE or DELETE
    :param msg: Text message to include in log entry for object action.
    
    """
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(object).pk,
        object_id = object.pk,
        object_repr = object.__unicode__(), # All models used here have __unicode__ methods.
        change_message = msg,
        action_flag = action,
    )

@basic_authentication
def pid(request, noid, type):
    '''REST API access to PURLs and ARKs.

    On GET, returns information about the PURL or ARK requested by id and type.
    
    Accessing an ARK or PURL will return all information associated with that
    pid.  In order to allow accessing and updating the unqualified (for an ARK)
    or default (for a PURL) target, the pid url must NOT include a trailing slash.
    Attempting to access a PURL pid as an ARK or vice versa will result in a 404.
    Example urls::

        http://pid.emory.edu/ark/8g3sq          - info for ARK and all targets
        http://pid.emory.edu/purl/127zr         - info for PURL and target

    On PUT, update a PURL or ARK.  Update values should be in the request body
    as JSON.  The following values are supported:
    
        * domain - domain, in URI resource format, e.g. http://pid.emory.edu/domain/1        
        * name - label or title
        * external_system_id - external system name
        * external_system_key - key or identifier in the specified external system
        * policy - policy by name (to specify a different policy from the default domain policy)

    Updating target information (resolve URI, active, proxy) is not currently
    supported via PUT on the Ark or Purl that the target belongs to.

    '''
    methods = ['GET', 'PUT']

    if request.method == 'DELETE':
        # *explicitly* disallow delete, since it will never be supported for pids
        response = HttpResponseNotAllowed(methods)
        response.content = '''ARKs and PURLs cannot be deleted.
If no longer in use, you may mark the target(s) as inactive, which will prevent
them from being resolved.'''
        return response

    # find the requested pid for view or update
    if request.method in methods:
        pid = get_object_or_404(Pid, pid__exact=noid, type=type.title())

    if request.method == 'PUT':
        if not request.user.is_authenticated():
            # 401 unauthorized - not logged in or invalid credentials
            return HttpResponseUnauthorized(BASIC_AUTH_REALM)
        elif not request.user.has_perm('pid.change_pid'):
            # 403 Forbidden - logged in but insufficient permissions
            return HttpResponseForbidden()

        # content should be posted in request body as JSON
        content_type = 'application/json'
        try:
            if request.META['CONTENT_TYPE'] != content_type:
                raise BadRequest("Unsupported content type '%s'; please use a supported format: %s" \
                                 % (request.META['CONTENT_TYPE'], content_type))

            # parse the request body as JSON
            data = json.loads(request.raw_post_data)

            # TODO: figure out how to take advantage of overlap in create_pid logic

            # update any pid properties that are specified
            if 'domain' in data:
                # domain should be passed in as resource URI
                pid.domain = _domain_from_uri(data['domain'])
            if 'name' in data:
                pid.name = data['name']
            if 'external_system_id' in data:
                # if external system id is set and not empty, find and update
                if data['external_system_id']:
                    try:
                        pid.ext_system = ExtSystem.objects.get(name=data['external_system_id'])
                    except ObjectDoesNotExist:
                        raise BadRequest("External System '%s' not found" % data['external_system_id'])
                # otherwise, clear external system
                else:
                    pid.ext_system = None
            if 'external_system_key' in data:
                pid.ext_system_key = data['external_system_key']
            if 'policy' in data:
                # if policy is set and not empty, find and update
                if data['policy']:
                    try:
                        pid.policy =  Policy.objects.get(title=data['policy'])
                    except ObjectDoesNotExist:
                        raise BadRequest("Policy '%s' not found" % request.POST['policy'])
                # otherwise, clear policy
                else:
                    pid.policy = None

            # NOTE: currently does not supporting target URI or info
            # It might be nice to allow updating one target specified by qualifier,
            # or perhaps only primary/default target, (roughly parallel to pid creation)
            # HOWEVER, that complicates things:
            # - should specifying active=True/False at this level apply to one
            #   target or ALL targets?
            # - if the requested target does not exist, do we create it?

            # set current user as editor
            pid.editor = request.user
            pid.save()
            _log_rest_action(request, pid, CHANGE,
                             'Updated pid:%s via rest api' % unicode(pid))

        except BadRequest as err:
            # return a response with status code 400, Bad Request
            return HttpResponseBadRequest('Error: %s' % err)

        # successful PUT can return 200 Ok or 204 No Content
        # in this case, on success, return the updated pid with status 200
        # -- fall through to common GET/PUT display logic

    # common logic for GET and successful PUT: return pid info as JSON
    if request.method == 'GET' or request.method == 'PUT':
        json_data = json_serializer.encode(pid_data(pid, request))
        return HttpResponse(json_data, mimetype='application/json')

    
    # if request method is not GET or PUT, return 405 method not allowed
    return HttpResponseNotAllowed(methods)

@basic_authentication
def target(request, noid, type, qualifier):
    '''REST API access to ARK and PURL targets.

    On GET, returns information about the PURL or ARK or target requested by id,
    type, and qualifier.  Returns information about the requested target only,
    with a reference to the ARK or PURL the target belongs to.  A final slash
    after the pid indicates that the unqualified or default target is requested.
    
    Examples urls::

        http://pid.emory.edu/purl/127zr/        - default (only) target (PURL)
        http://pid.emory.edu/ark/8g3sq/         - unqualified ARK target
        http://pid.emory.edu/ark/8g3sq/qual     - qualified ARK target

    On PUT, update or create the target requested.  If a target with the requested
    qualifier exists, it will be updated; if it does not exist, a new target
    will be created with the requested qualifier and the specified information.

    Update values should be in the request body as JSON.  The following values
    are supported:
    
        * proxy - name of the proxy to use when resolving; set blank to clear proxy
        * target_uri - URI that the target should resolve to when accessed
        * active - boolean; indicates whether or not the target should be resolved

    On DELETE, remove the target.  Delete is **only** allowed for ARK targets.

    '''
    methods = ['GET', 'PUT']
    # target deletion is allowed for ARK targets only
    if type == 'ark':
        methods.append('DELETE')
        
    # target filter options to find the requested target for view or update
    target_details = {
        'noid__exact': noid,
        'qualify': qualifier,
        'pid__type': type.title()
    }
    status = 200

    if request.method == 'PUT':
        if not request.user.is_authenticated():
            # 401 unauthorized - not logged in or invalid credentials
            return HttpResponseUnauthorized(BASIC_AUTH_REALM)

        # content should be posted in request body as JSON
        content_type = 'application/json'
        try:
            # retrieve an existing target or create a new one
            try:
                target = Target.objects.get(**target_details)
                new_target = False
            except ObjectDoesNotExist:
                # if the target with the requested qualifier does not exist, create it
                pid = get_object_or_404(Pid, pid__exact=noid, type=type.title())
                target = pid.target_set.create(qualify=qualifier)
                new_target = True
                status = 201 # Created

            # check permissions according to action being done:
            if (new_target and not request.user.has_perm('pid.add_target')) or \
                (not new_target and not request.user.has_perm('pid.change_target')):
                # 403 Forbidden - logged in but insufficient permissions
                return HttpResponseForbidden()

            if request.META['CONTENT_TYPE'] != content_type:
                raise BadRequest("Unsupported content type '%s'; please use a supported format: %s" \
                                 % (request.META['CONTENT_TYPE'], content_type))
            # parse the request body as JSON
            data = json.loads(request.raw_post_data)
            # TODO: figure out how to take advantage of overlap in create_pid logic

            # update any target properties that are specified
            if 'proxy' in data:
                # if proxy is set and not empty, look up proxy
                if data['proxy']:
                    try:
                        target.proxy = Proxy.objects.get(name=data['proxy'])
                    except ObjectDoesNotExist:
                        raise BadRequest("Proxy '%s' not found" % data['proxy'])
                # otherwise - remove proxy
                else:
                    target.proxy = None
            if 'target_uri' in data:
                target.uri = data['target_uri']
            if 'active' in data:
                target.active = data['active']

            target.save()
            # updating or adding a target counts as editing a pid
            # - update pid to set current user as editor
            target.pid.editor = request.user
            target.pid.save()
            _log_rest_action(request, target, CHANGE,
                 'Updated target:%s via rest api' % unicode(target))
            _log_rest_action(request, target.pid, CHANGE,
                 'Updated pid:%s via rest api' % unicode(target.pid))
            
            # on success, fall through to common GET/PUT display logic

        except BadRequest as err:
            # return a response with status code 400, Bad Request
            return HttpResponseBadRequest('Error: %s' % err)

    # find the requested target
    if request.method == 'GET':
        target = get_object_or_404(Target, **target_details)

    # common logic for GET and successful PUT: return target info as JSON
    if request.method == 'GET' or request.method == 'PUT':
        data = target_data(target, request)
        data['pid'] = request.build_absolute_uri(reverse('rest_api:pid',
                                        kwargs={'noid': target.noid,
                                                'type': target.pid.type.lower()}))
        json_data = json_serializer.encode(data)
        return HttpResponse(json_data, mimetype='application/json', status=status)

    # ARK targets can be deleted; PURLs have only one target-- not allowing deletion
    if request.method == 'DELETE' and type == 'ark':
        # check permissions before deleting
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized(BASIC_AUTH_REALM)
        elif not request.user.has_perm('pid.delete_pid'):
            return HttpResponseForbidden()
        
        target = get_object_or_404(Target, **target_details)
        # action must be logged before the object is deleted
        _log_rest_action(request, target, DELETION,
                 'Deleted target:%s via rest api' % unicode(target))
        target.delete()        
        # consider deleting a target as an update to the ARK
        target.pid.editor = request.user
        target.pid.save()
        _log_rest_action(request, target.pid, CHANGE,
                 'Updated pid:%s via rest api - deleted target %s' % \
                 (unicode(target.pid), unicode(target)))
        # on successful delete, send 200 OK (NOT 410 Gone because that would be ambiguous)
        return HttpResponse(status=200)

    # if request method is not implemented, return 405 method not allowed
    return HttpResponseNotAllowed(methods)



@basic_authentication
def create_pid(request, type):
    '''On POST, create a new ARK or PURL.  On successful creation, returns a 
    response with status code 201 (Created), and response content is the resolvables
    url for the newly minted ARK or PURL.  If required parameters are missing
    or any parameters are invalid (e.g., referencing a Proxy or Policy that does
    not exist), the returned response will have a status code 400 (Bad Request),
    and the content of the response will be an explanatory message.

    Supported POST parameters
    
        * domain - REQUIRED; domain should be in URI resource format, e.g.
          http://pid.emory.edu/domain/1
        * target_uri - REQUIRED; URL that the new ARK or PURL should resolve to
        * name - label or title for the new pid
        * external_system_id - external system name
        * external_system_key - key or identifier in the specified external system
        * policy - policy by name (if this pid needs a different policy from its
          domain)
        * proxy - proxy to use when resolving target url; specify by name
        * qualifier - target should be created with the specified target;**ARK only**

    :param type: type of pid to create - ark or purl
    
    '''
    if request.method == 'POST':
        # TODO: require ssl ?
        if not request.user.is_authenticated():
            # 401 unauthorized - not logged in or invalid credentials
            return HttpResponseUnauthorized(BASIC_AUTH_REALM)
        elif not request.user.has_perm('pid.add_pid'):
            # 403 Forbidden - logged in but insufficient permissions
            return HttpResponseForbidden()

        try:
            # if required fields are not present, return an error message
            if 'domain' not in request.POST or 'target_uri' not in request.POST:
                raise BadRequest('domain and target_uri are required')
            # incompatible options - qualifier only makes sense for purls
            if 'qualifier' in request.POST and type == 'purl':
                raise BadRequest('Purl targets can not have qualifiers')
            
            # domain should be passed in as resource URI - resolve to model instance
            domain = _domain_from_uri(request.POST['domain'])

            # assemble the data for creating the new pid
            # - required fields
            pid_opts = {
                'type': type.title(),  # url uses lower case, model requires title case
                'domain': domain,
                'creator_id': request.user.id,
                'editor_id': request.user.id
                }
            # - optional fields
            if 'name' in request.POST:
                pid_opts['name'] = request.POST['name']
            # could you have an external system id and not a ext-sys key? or vice versa?
            if 'external_system_id' in request.POST:
                try:
                    pid_opts['ext_system'] = ExtSystem.objects.get(name=request.POST['external_system_id'])
                except ObjectDoesNotExist:
                    raise BadRequest("External System '%s' not found" % request.POST['external_system_id'])
            if 'external_system_key' in request.POST:
                pid_opts['ext_system_key'] = request.POST['external_system_key']
            if 'policy' in request.POST:
                try:
                    pid_opts['policy'] =  Policy.objects.get(title=request.POST['policy'])
                except ObjectDoesNotExist:
                    raise BadRequest("Policy '%s' not found" % request.POST['policy'])

            # target can't be created until after the noid is minted
            # - init target options before creating pid to be sure they are valid
            #   (i.e., if a proxy is specified, it exists)
            target_opts = {'uri': request.POST['target_uri']}
            if 'proxy' in request.POST:
                try:
                    target_opts['proxy'] = Proxy.objects.get(name=request.POST['proxy'])
                except ObjectDoesNotExist:
                    raise BadRequest("Proxy '%s' not found" % request.POST['proxy'])
            if 'qualifier' in request.POST:
                # an invalid qualifier would normally get caught when a target is saved
                # checking here to avoid creating a new Pid if the qualifier is invalid
                if not valid_qualifier(request.POST['qualifier']):
                    raise BadRequest("Qualifier '%s' contains invalid characters" % request.POST['qualifier'])
                target_opts['qualify'] = request.POST['qualifier']

            # create the pid, and then save to mint the noid before target is created
            p = Pid(**pid_opts)
            p.save()
            _log_rest_action(request, p, ADDITION, 'Added pid:%s via rest api' % p.__unicode__())
            t = p.target_set.create(**target_opts)
            _log_rest_action(request, t, ADDITION, 'Added target:%s for pid:%s via rest api' % (t.__unicode__(), p.__unicode__()))

            # return the resolvable url (purl/ark) for the new target
            return HttpResponse(t.get_resolvable_url(), status=201)   # 201 Created
        
        except BadRequest as err:
            # return a response with status code 400, Bad Request
            return HttpResponseBadRequest('Error: %s' % err)


    # if request method is not POST, return 405 method not allowed
    return HttpResponseNotAllowed(['POST'])

def search_pids(request):
    '''On GET, searches pids based on key-value querystring values and returns
    a list of pids in JSON format.

    Querystring format should be as follows::

        /pids/?<querystring parts>

    querystring parts are standard urlencoded &key=value pairs.  None are
    required but at least one is required to perform a search actionable
    querystring values for searching are:

        * domain - exact domain uri for pid
        * type - purl or ark
        * pid - exact pid value
        * target - exact target uri
        
    '''
    # Only build searches on the following params.
    valid_search_params = {
        'domain': 'domain__name__iexact',
        'type': 'type__iexact',
        'pid': 'pid__iexact',
        'target': 'target__uri__exact',
    }

    query = {} # Initialize the query dict

    # Create the param searches as dict values
    for param in valid_search_params:
        if request.GET.has_key(param):
            query[valid_search_params[param]] = request.GET.get(param)

    # Qualifier is handled somewhat differently in that it might be empty.
    # Add either an isnull search or exact search to the query dict as needed.
    if request.GET.has_key('qualifier'):
        qualifier = request.GET.get('qualifier')
        if qualifier == '':
            query['target__qualifier__isnull'] = 'True'
        elif len(qualifier) > 0:
            query['target__qualifier__exact'] = qualifier

    # Return the queryset or default to list of all pids ordered by last update
    pid_list = Pid.objects.filter(**query).order_by('updated_at')
    if not query:
        pid_list = Pid.objects.all().order_by('updated_at')

    # pagination code based on the django documentation for same
    # Make sure page and count are set to default values if empty and are int
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        count = int(request.GET.get('count', 10))
    except ValueError:
        count = 10

    # Setup paging of results on the queryset.
    paginator = Paginator(pid_list, count)

    # If page request (9999) is out of range, deliver last page of results.
    try:
        pids = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pids = paginator.page(paginator.num_pages)

    # Get a list of pids converted to dicts for json converstion
    pids = [pid_data(pid, request) for pid in pids.object_list]

    json_data = json_serializer.encode(pids)
    return HttpResponse(json_data, mimetype='application/json')

@basic_authentication
def domains(request):
    '''On GET, returns a list of all top-level :class:`pidman.pid.models.Domain`
    instances.  Subdomains/collections, if any, will be listed under the domain
    they belong to.

    On POST, create a new Domain.  On successful creation, returns a
    response with status code 201 (Created), If required parameters are missing
    or any parameters are invalid (e.g., referencing a parent Domain or Policy that does
    not exist), the returned response will have a status code 400 (Bad Request),
    and the content of the response will be an explanatory message.

    Supported POST parameters:
        * name -  - REQUIRED: label or title for the new  Domain
        * policy - policy title
        * parent - parent uri
        
    '''
    methods = ['GET', 'POST']
    
    if request.method == 'GET':
        # retrieve all top-level domains
        domains = Domain.objects.filter(parent=None)
        data = [domain_data(d, request) for d in domains]
        json_data = json_serializer.encode(data)
        return HttpResponse(json_data, mimetype='application/json')

    elif request.method == 'POST':
        #Validate permissions
        if not request.user.is_authenticated():
            # 401 unauthorized - not logged in or invalid credentials
            return HttpResponseUnauthorized(BASIC_AUTH_REALM)
        elif not request.user.has_perm('pid.add_domain'):
            # 403 Forbidden - logged in but insufficient permissions
            return HttpResponseForbidden()

        # create domain with provided name
        domain_opts = {} # options used to create the domain

        try:
            if 'name' in request.POST and request.POST['name'].strip():
                domain_opts['name'] = request.POST['name']
            else:
                raise BadRequest('name is required')

        except BadRequest as err:
            return HttpResponse('Error: %s' % err, status=400)   # 400 = Bad Request


        #get parent if parent is in POST
        try:
            if 'parent' in request.POST and request.POST['parent'].strip():
                domain_opts['parent'] =  _domain_from_uri(request.POST['parent'])
        except BadRequest as err:
            return HttpResponse("Error: Parent %s does not exists" % request.POST['parent'], status=400)   #400 = Bad Request


        #get policy if policy is in POST
        try:
            if 'policy' in request.POST and request.POST['policy'].strip():
                    domain_opts['policy'] =  Policy.objects.get(title=request.POST['policy'])
        except ObjectDoesNotExist as err:
            return HttpResponse("Error: Policy %s does not exists" % request.POST['policy'], status=400)   #400 = Bad Request


        try:
            domain, created = Domain.objects.get_or_create(**domain_opts)
            if created:
                status = 201 #201 = Created
                msg = ""

                #log the creation of a new Domain
                _log_rest_action(request, domain, ADDITION, 'Added Domain:%s via rest api' % domain.__unicode__())

            else:
                status = 400 # Bad Request -  in this case the object already exists
                msg = "Error: Domain '%s' already exists" % request.POST['name']

            return HttpResponse(msg, status = status)

        except IntegrityError as err:
            return HttpResponse("Error: Domain '%s' already exists" % request.POST['name'], status=400)   #400 = Bad Request
        # Will catch any othr random error
        except Exception as err:
            return HttpResponse("Error: %s " % err, status=500)   #500 = Bad Request

    # if request method is not GET, return 405 method not allowed 
    return HttpResponseNotAllowed(methods)

@basic_authentication
def domain(request, id):
    '''On GET, return information about the `pidman.pid.models.Domain`
    instance specified by id.  Includes information about subdomains/collections
    (if any), as well as parent domain URI (if any).

    On PUT, update Domain.  Update values should be in the request body
    as JSON.  The following values are supported:
        * name - label or title for the Domain
        * policy - policy title
        * parent - parent uri
    '''
    # Look-Up object for PUT and GET
    if request.method == 'GET' or  request.method == 'PUT':
	domain = get_object_or_404(Domain, id__exact=id)
        
    if request.method == 'PUT':
        #Validate permissions
        if not request.user.is_authenticated():
            # 401 unauthorized - not logged in or invalid credentials
            return HttpResponseUnauthorized(BASIC_AUTH_REALM)
        elif not request.user.has_perm('pid.change_domain'):
            # 403 Forbidden - logged in but insufficient permissions
            return HttpResponseForbidden()

        # content should be posted in request body as JSON
        content_type = 'application/json'
        try:

       	    if request.META['CONTENT_TYPE'] != content_type:
        	raise BadRequest("Unsupported content type '%s'; please use a supported format: %s" \
                                 % (request.META['CONTENT_TYPE'], content_type))
            # parse the request body as JSON
            data = json.loads(request.raw_post_data)

            if len(data) == 0:
                raise BadRequest("No Parameters Passed")

            #set new values and save
            if 'name' in data:
                domain.name = data['name']
            if 'parent' in data and data['parent']:
                    try:
                        domain.parent =  _domain_from_uri(data['parent'])
                    except ObjectDoesNotExist:
                        raise BadRequest("Parent Domani '%s' not found" % data['parent'])
            else:
                domain.parent =  None
            if 'policy' in data and data['policy']:
                    try:
                        domain.policy =  Policy.objects.get(title=data['policy'])
                    except ObjectDoesNotExist:
                        raise BadRequest("Policy '%s' not found" % data['policy'])
            else:
                domain.policy =  None

            domain.save()
            _log_rest_action(request, domain, CHANGE, 'Updated Domain: %s via rest api' % domain.__unicode__())

        except BadRequest as err:
            # return a response with status code 400, Bad Request
            return HttpResponseBadRequest('Error: %s' % err)

    #return Domain object for both GET or PUT
    if request.method == 'GET' or request.method == 'PUT':
        json_data = json_serializer.encode(domain_data(domain, request))
        return HttpResponse(json_data, mimetype='application/json')
       
    # if request method is not GET or PUT, return 405 method not allowed
    return HttpResponseNotAllowed(['GET', 'PUT'])





def pid_data(pid, request):
    '''Generate a dictionary of data for a :class:`pidman.pid.models.Pid` for
    REST API dissemination.  Includes the REST resource URI for the Pid.

    :param pid: :class:`pidman.pid.models.Pid` instance
    :param request: :class:`django.http.HttpRequest`, for generating absolute URIs
    :rtype: dict
    '''
    data = {
        'uri': request.build_absolute_uri(reverse('rest_api:pid',
                    kwargs={'noid':pid.pid, 'type': pid.type.lower()})),
        'pid': pid.pid,
        'domain': request.build_absolute_uri(reverse('rest_api:domain',
                    kwargs={'id':pid.domain.id})),
        'creator': pid.creator.username,
        'created': pid.created_at.isoformat(), 
        'editor': pid.editor.username,
        'updated': pid.updated_at.isoformat(),
        'targets': [target_data(t, request) for t in pid.target_set.all()]
    }
    # name is optional, only include if set
    if pid.name:
        data['name'] = pid.name

    # include policy information only if one is set
    if pid.policy:
        # Policy titles are required to be unique, so this should be OK.
        # It might be better to include title and uri, but policies are
        # currently not planned to be exposed via REST api.
        data['policy'] = pid.policy.title

    # include external system information only if one is set
    if pid.ext_system or pid.ext_system_key:
        # External System names are also required to be unique
        data['external_system'] = {
            'id': pid.ext_system.name,
            'key': pid.ext_system_key
        }
    return data

def target_data(target, request):
    '''Generate a dictionary of data about a single :class:`pidman.pid.models.Target`
    for REST API dissemination.  Includes the Target resource URI.

    :param target: :class:`pidman.pid.models.Target` instance
    :param request: :class:`django.http.HttpRequest`, for generating absolute URI
    :rtype: dict
    '''
    # build rest api resource uri appropriately based on type of pid
    if target.pid.type == 'Ark':
        rest_uri = reverse('rest_api:ark-target',
                           kwargs={'noid': target.noid, 'qualifier': target.qualify})
    else:
        rest_uri = reverse('rest_api:purl-target', kwargs={'noid': target.noid})

    data = {
        'uri': request.build_absolute_uri(rest_uri),
        'access_uri': target.get_resolvable_url(),
        'target_uri': target.uri,
        'active': target.active
    }
    if target.qualify:
        data['qualifier'] = target.qualify
    if target.proxy:
        data['proxy'] = target.proxy.name
    return data

def domain_data(domain, request):
    '''Generate a dictionary of data about a single :class:`pidman.pid.models.Domain`
    and any collections that belong to it, for REST API dissemination.  Includes
    Domain resource URI.

    :param domain: :class:`pidman.pid.models.Domain` instance
    :param request: :class:`django.http.HttpRequest`, for generating absolute URI
    :rtype: dict
    '''
    data = {
        'uri': request.build_absolute_uri(reverse('rest_api:domain',
                    kwargs={'id': domain.id})),
        'name': domain.name,
        'updated': domain.updated_at.isoformat(),
        'number of pids': domain.num_pids()
    }
    if domain.policy:
        data['policy'] = domain.policy.title
    
    if domain.parent:
        # if this domain has a parent, it is a collection/subdomain
        # include parent domain uri
        data['domain'] = request.build_absolute_uri(reverse('rest_api:domain',
                                    kwargs={'id': domain.parent.id}))

    if domain.collections.count():
        # if this domain has collections, include them as a list
        data['collections'] = [domain_data(d, request) for d in domain.collections.all()]

    return data


def _domain_from_uri(domain_uri):
    '''Resolve a domain resource URI into a :class:`pidman.pid.models.Domain`
    instance.  Raises a :class:`BadRequest` if the URI cannot be parsed, cannot
    be resolved as a domain URI, or if the requested domain does not exist.

    :param domain_uri: domain resource URI, e.g. http://pid.emory.edu/domain/1
    :rtype: :class:`pidman.pid.models.Domain`
    '''
    # domain should be passed in as resource URI
    # - resolve the uri to get domain id and retrieve domain object
    try:
        parsed_domain_uri = urlparse(domain_uri)
        # resolve the local part of the url using django url resolver
        # returns a tuple of view function, args, kwargs (as of django 1.2)
        view_function, args, kwargs = resolve(parsed_domain_uri.path)
    except Exception:
        # any exception parsing or resolving the domain - Bad Request
        raise BadRequest('Could not resolve domain URI %s' % domain_uri)

    # at this point the domain has been parsed as a url and resolved;
    # make sure it resolves to domain view method and has an id
    if view_function is not domain or 'id' not in kwargs:
        # if the uri does not resolve to the rest api domain method
        # or does not have an id argument, it's not a domain uri
        raise BadRequest('Could not resolve domain URI into a domain')
    
    try:
        d = Domain.objects.get(pk=kwargs['id'])
    except ObjectDoesNotExist:
        raise BadRequest("Could not find Domain for URI %s" % domain_uri)

    return d
