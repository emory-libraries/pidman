from django.contrib.auth import authenticate
from eulcore.django.soap.app import DjangoSoapApp, soapmethod, soap_types
from pidman.pid.models import Pid, Target, Proxy, ExtSystem, Domain, parse_resolvable_url

ERR_NOT_AUTHORIZED = 'request canceled: not authorized'

def create_pid(domain_id, user, name, type, uri, qualifier='', proxy_id=None,
    external_system_name=None, external_system_key=None, **kwargs):
    '''Convenience function to create new ark or purl with a single target.
    Handles all the look-ups for related objects to be associated with the new
    :class:`~pidman.pid.models.Pid`.

    Common functionality for :meth:`PersistentIdentifierService.GenerateArk`
    and :meth:`PersistentIdentifierService.GeneratePurl`.

    :returns: :class:`~pidman.pid.models.Target` - the single target created
        for the new :class:`~pidman.pid.models.Pid`
    '''
    d = Domain.objects.get(pk=domain_id)
                    
    # if external_system is specified, find ExtSystem by name
    if (external_system_name):
        extsys = ExtSystem.objects.get(name__exact=external_system_name)
    else:
        extsys = None

    # name is optional; convert nulls to empty string
    if name == None:
        name = ''

    # NOTE: currently setting creator as editor - mirrors behavior of rails app
    p = Pid(domain=d, name=name, type=type, creator=user, editor=user,
            ext_system=extsys, ext_system_key=external_system_key)
    p.save()    # mint noid & save new pid to db

    # if proxy was specified, find for ark creation
    if (proxy_id):
        proxy = Proxy.objects.get(pk=proxy_id)
    else:
        proxy = None
    # if qualifier is None, must be set to '' for primary target to be found properly
    if (qualifier == None):
        qualifier = ''
    t = p.target_set.create(qualify=qualifier, uri=uri, proxy=proxy)        
    return t

# added new create_pid method to include active flag
# TODO: this method is redundant and should be consolidated with create_pid or removed entirely
def create_pid_active(domain_id, user, name, type, uri, qualifier='', proxy_id=None,
    active=True, external_system_name=None, external_system_key=None, **kwargs):
    d = Domain.objects.get(pk=domain_id)
                    
    # if external_system is specified, find ExtSystem by name
    if (external_system_name):
        extsys = ExtSystem.objects.get(name__exact=external_system_name)
    else:
        extsys = None

    # name is optional; convert nulls to empty string
    if name == None:
        name = ''

    # NOTE: currently setting creator as editor - mirrors behavior of rails app
    p = Pid(domain=d, name=name, type=type, creator=user, editor=user,
            ext_system=extsys, ext_system_key=external_system_key)
    p.save()    # mint noid & save new pid to db

    # if proxy was specified, find for ark creation
    if (proxy_id):
        proxy = Proxy.objects.get(pk=proxy_id)
    else:
        proxy = None
        
    # if qualifier is None, must be set to '' for primary target to be found properly
    if (qualifier == None):
        qualifier = ''
              
    t = p.target_set.create(qualify=qualifier, uri=uri, proxy=proxy, active=active)        
    return t

class PersistentIdentifierService(DjangoSoapApp):

    # FIXME: what is the proper namespace to use? needs to match rails app
    #__tns__ = 'urn:ActionWebService'
    
    @soapmethod(soap_types.String,  # username
                soap_types.String,  # password
                soap_types.String,  # uri
                soap_types.String,  # name
                soap_types.String,  # qualifier
                soap_types.Integer, # domain id
                soap_types.Integer, # proxy id
                soap_types.String,  # external system name
                soap_types.String,  # external system key
        _returns=soap_types.String,
        _outVariableName='return')
    def GenerateArk(self, username, password, uri, name, qualifier, domain_id, proxy_id,
                    external_system, external_system_key):
        '''Create a new ARK with a single target. Returns the resolvable form
        of the full ARK, with any qualifier that was specified.
        
        :param username: user login
        :param password: user password
        :param uri: target URI for the new ARK
        :param name: title or label for the new ARK
        :param qualifier: qualifier for the new ARK (empty string for unqualified)
        :param domain_id: numeric id for the :class:`~pid.pidman.models.Domain`
            the new ARK should belong to
        :param proxy_id: numeric id for the :class:`~pid.pidman.models.Proxy`
            that the new ARK target should use for resolving, or blank for none
        :param external_system: name of an :class:`~pid.pidman.models.ExtSystem`,
            or blank for none
        :param external_system_key: key or identifier in the specified external system
        '''
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception(ERR_NOT_AUTHORIZED)

        # create pid with type purl and all parameters
        t = create_pid(type="Ark", user=user, uri=uri, name=name, qualifier=qualifier,
            domain_id=domain_id, proxy_id=proxy_id, external_system_name=external_system,
            external_system_key=external_system_key)
        
        # return the resolvable url for the target that was just created
        return t.get_resolvable_url()

    @soapmethod(soap_types.String,  # username
                soap_types.String,  # password
                soap_types.String,  # noid
                soap_types.String,  # qualifier
                soap_types.String,  # uri
                soap_types.Integer, # proxy_id
                _returns=soap_types.String,
                _outVariableName='return')
    def AddArkTarget(self, username, password, noid, qualifier, uri, proxy_id):
        '''Add a new :class:`~pidman.pid.models.Target` to an existing ARK and
        return the resolvable url for the new target.
        
        :param username: user login
        :param password: user password
        :param noid: NOID portion of the ARK for the :class:`~pidman.pid.models.Pid`
            instance the target should be added to
        :param qualifier: qualifier for the new ARK (empty string for unqualified)
        :param uri: URI for the new target
        :param proxy_id: numeric id for the :class:`~pid.pidman.models.Proxy`
            that the new ARK target should use for resolving, or blank for none
        '''
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception(ERR_NOT_AUTHORIZED)
            
        # This is a fix, to make a null and empty string.
        if (qualifier is None):
            qualifier = ''            

        p = Pid.objects.get(pid__exact=noid)
        if (proxy_id):
            proxy = Proxy.objects.get(pk=proxy_id)
        else:
            proxy = None
        p.save()
        # FIXME: what is supposed to happen if the target already exists?
        # should cause an error (and does - violates db constraint)
        # MAY want to catch this and return a nicer/more readable error...
        t = p.target_set.create(qualify=qualifier, uri=uri, proxy=proxy)
        
        # NOTE: adding a target via soap does not currently set pid editor & updated_at values
        # (this appears to be the same as the behavior of rails app)
        
        # return the resolvable url for the target that was just created
        return t.get_resolvable_url()

    @soapmethod(soap_types.String,  # username
                soap_types.String,  # password
                soap_types.String,  # uri
                soap_types.String,  # name
                soap_types.Integer, # domain id
                soap_types.Integer, # proxy id
                soap_types.String,  # external system name
                soap_types.String,  # external system key
                _returns=soap_types.String,
                _outVariableName='return')
    def GeneratePurl(self, username, password, uri, name, domain_id, proxy_id,
                     external_system, external_system_key):
        '''Generate a new PURL for the specified url and return it.

        :param username: user login
        :param password: user password
        :param uri: target URI for the new PURL
        :param name: title or label for the new PURL
        :param domain_id: numeric id for the :class:`~pid.pidman.models.Domain`
            the new PURL should belong to
        :param proxy_id: numeric id for the :class:`~pid.pidman.models.Proxy`
            that the new PURL target should use for resolving, or blank for none
        :param external_system: name of an :class:`~pid.pidman.models.ExtSystem`,
            or blank for none
        :param external_system_key: key or identifier in the specified external system
        '''
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception(ERR_NOT_AUTHORIZED)

        # create pid with type purl and no qualifier
        t = create_pid(type="Purl", user=user, uri=uri, name=name,
            domain_id=domain_id, proxy_id=proxy_id, external_system_name=external_system,
            external_system_key=external_system_key)
        return t.get_resolvable_url()

    @soapmethod(soap_types.String,  # username
                soap_types.String,  # password
                soap_types.String,  # purl (full purl, ark, or qualified ark)
                soap_types.String,  # uri
                _returns=soap_types.String,
                _outVariableName='return')
    def EditTarget(self, username, password, purl, uri):
        '''Update the target for an existing ARK or PURL and return the PURL or
        qualified ARK that was updated.
        
        :param username: user login
        :param password: user password
        :param purl: full, URL resolvable form of the PURL, ARK, or qualified
            ARK to be updated
        :param uri: updated URI 
        '''
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception(ERR_NOT_AUTHORIZED)

        # NOTE that purl parameter is full purl OR full ark (could be a qualified ark)

        # parse purl/ark into component parts in order to find the appropriate target
        info = parse_resolvable_url(purl)        
        t = Target.objects.filter(noid__exact=info['noid']).filter(qualify__exact=info['qualifier']).get()        
        t.uri = uri
        # FIXME: update editor/modified date?
        t.save()
        
        # return the resolvable url for the target that was just updated
        return t.get_resolvable_url()

	# added new GenerateArkActive method to include active flag
    @soapmethod(soap_types.String,  # username
                soap_types.String,  # password
                soap_types.String,  # uri
                soap_types.String,  # name
                soap_types.String,  # qualifier
                soap_types.Integer, # domain id
                soap_types.Integer, # proxy id
                soap_types.Boolean, # active
                soap_types.String,  # external system name
                soap_types.String,  # external system key
        _returns=soap_types.String,
        _outVariableName='return')
    def GenerateArkActive(self, username, password, uri, name, qualifier, domain_id, proxy_id, active,
                    external_system, external_system_key):
        """Create a new ark with a single target and return the full ark (with qualifier if specified)"""
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception(ERR_NOT_AUTHORIZED)

        # create pid with type purl and all parameters
        t = create_pid_active(type="Ark", user=user, uri=uri, name=name, qualifier=qualifier,
            domain_id=domain_id, proxy_id=proxy_id, active=active, external_system_name=external_system,
            external_system_key=external_system_key)
        
        # return the resolvable url for the target that was just created
        return t.get_resolvable_url()

	# added new AddArkTargetActive method to include active flag
    @soapmethod(soap_types.String,  # username
                soap_types.String,  # password
                soap_types.String,  # noid
                soap_types.String,  # qualifier
                soap_types.String,  # uri
                soap_types.Integer, # proxy_id
                soap_types.Boolean, # active
                _returns=soap_types.String,
                _outVariableName='return')
    def AddArkTargetActive(self, username, password, noid, qualifier, uri, proxy_id, active):
        """Add a new target to an existing ark and return resolvable url for the new target"""
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception(ERR_NOT_AUTHORIZED)

        p = Pid.objects.get(pid__exact=noid)
        if (proxy_id):
            proxy = Proxy.objects.get(pk=proxy_id)
        else:
            proxy = None
        p.save()
        # FIXME: what is supposed to happen if the target already exists?
        # should cause an error (and does - violates db constraint)
        # MAY want to catch this and return a nicer/more readable error...
        t = p.target_set.create(qualify=qualifier, uri=uri, proxy=proxy, active=active)
        
        # NOTE: adding a target via soap does not currently set pid editor & updated_at values
        # (this appears to be the same as the behavior of rails app)
        
        # return the resolvable url for the target that was just created
        return t.get_resolvable_url()

	# added new GeneratePurlActive method to include active flag
    @soapmethod(soap_types.String,  # username
                soap_types.String,  # password
                soap_types.String,  # uri
                soap_types.String,  # name
                soap_types.Integer, # domain id
                soap_types.Integer, # proxy id
                soap_types.Boolean, # active
                soap_types.String,  # external system name
                soap_types.String,  # external system key
                _returns=soap_types.String,
                _outVariableName='return')
    def GeneratePurlActive(self, username, password, uri, name, domain_id, proxy_id, active, external_system, external_system_key):
        """Generate a new purl for the specified url and return the purl"""
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception(ERR_NOT_AUTHORIZED)

        # create pid with type purl and no qualifier
        t = create_pid_active(type="Purl", user=user, uri=uri, name=name,
            domain_id=domain_id, proxy_id=proxy_id, active=active, external_system_name=external_system,
            external_system_key=external_system_key)
        return t.get_resolvable_url()

	# added new EditTargetActive method to include active flag
    @soapmethod(soap_types.String,  # username
                soap_types.String,  # password
                soap_types.String,  # purl (full purl, ark, or qualified ark)
                soap_types.Boolean,  # active
                _returns=soap_types.String,
                _outVariableName='return')
    def EditTargetActive(self, username, password, purl, active):
        """Update the target active flag for an existing ark or purl and return the purl or qualified ark that was updated"""
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception(ERR_NOT_AUTHORIZED)

        # NOTE that purl parameter is full purl OR full ark (could be a qualified ark)

        # parse purl/ark into component parts in order to find the appropriate target
        info = parse_resolvable_url(purl)        
        t = Target.objects.filter(noid__exact=info['noid']).filter(qualify__exact=info['qualifier']).get()        
        t.active = active
        # FIXME: update editor/modified date?
        t.save()
        
        # return the resolvable url for the target that was just updated
        return t.get_resolvable_url()

pid_service = PersistentIdentifierService()
