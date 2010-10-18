import os
import re
import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import connection, models

from linkcheck import Linklist
from linkcheck.models import Link as LinkCheckLink

from pidman.pid.ark_utils import normalize_ark, valid_qualifier, qualifier_allowed_characters
from pidman.pid.noid import encode_noid
from django.core.exceptions import ValidationError

def mint_noid():
    '''mint_noid() -> unicode
    Generate a new NOID (Nice Opaque IDentifier).
    '''
    cursor = connection.cursor()
    cursor.execute("SELECT nextval('pid_pid_pid_seq')")
    noid_num = cursor.fetchone()[0]
    cursor.close()

    return encode_noid(noid_num)


class ExtSystemManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class ExtSystem(models.Model):
    '''External System.  Use this model to define an External Systems that
    will be used with :class:`Pid` instances, so that users can store an
    associated identifier from an external system on a :class:`Pid` instance.'''
    name = models.CharField(unique=True, max_length=127)
    key_field = models.CharField(max_length=127)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExtSystemManager()

    class Meta:
        verbose_name = "External System"

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    
class PolicyManager(models.Manager):
    def get_by_natural_key(self, title):
        return self.get(title=title)

class Policy(models.Model):
    '''A policy that defines the commitment level for :class:`Pid` instances.
    Can be associated with :class:`Domain` or :class:`Pid`.

    The Policy is used for ARK metadata exposed via the resolver; see section
    5.1.1 of the ARK specification.
    '''
    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    commitment = models.TextField("Commitment Statement")
    title      = models.CharField(unique=True, max_length=255)

    objects = PolicyManager()

    class Meta:
        verbose_name_plural = "Policies"

    def __unicode__(self):
        return self.commitment

    def natural_key(self):
        return (self.title,)

class DomainException(Exception):
    pass

# NOTE: not adding natural key logic to Target because it results in a dependency
# error, most likely because of Domain -> collection/subdomain recursive relation.

class Domain(models.Model):
    '''A Domain is a collection of :class:`Pid` instances.  Domains can have an
    associated :class:`Policy`, which all Pids in that collection inherit by
    default.  This implementation allows for collections or subdomains
    that belong to a domain (currently only supports one level of nesting).
    
    Domains are **not** part of the ARK spec, but a feature of this implementation
    meant for managing and grouping PIDs.
    '''
    name = models.CharField(unique=True, max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    policy = models.ForeignKey(Policy, blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True,
                related_name='collections', db_column='parent_id')
  
    def __unicode__(self):
        return self.name

    def get_policy(self):
        '''Return the policy for this domain or from parent domain if inherited.
        Raises a :class:`DomainException` if no policy is found.
        
        :return: instance of :class:`Policy`
        '''
        if self.policy:
            return self.policy
        elif self.parent:
            return self.parent.get_policy()
        else:
            raise DomainException("No Policy Exists")

    def num_collections(self):
        "Number of collections under this domain."
        return self.collections.count()
    num_collections.short_description = "# collections"

    def num_pids(self):
        '''Number of :class:`Pid` instances in this domain, including those in
        any subdomains.'''
        pid_count = self.pid_set.count()
        for subdomain in self.collections.all():
            pid_count += subdomain.pid_set.count()
        return pid_count
    num_pids.short_description = "# pids"

class PidManager(models.Manager):
    def get_by_natural_key(self, noid):
        return self.get(pid=noid)

class Pid(models.Model):
    '''Pid: an ARK or a PURL, with associated :class:`Target` instance(s).'''
    pid = models.CharField(unique=True, max_length=255, editable=False, default=mint_noid)
    domain = models.ForeignKey(Domain)
    name = models.CharField(max_length=1023, blank=True)
    # external system & key - identifier in another system, e.g. EUCLID control key
    ext_system = models.ForeignKey(ExtSystem, verbose_name='External system', blank=True, null=True)
    ext_system_key = models.CharField('External system key', max_length=1023, blank=True, null=True)
    creator = models.ForeignKey(User, related_name='created')
    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    editor = models.ForeignKey(User, related_name="edited")
    pid_types = (("Ark", "Ark"), ("Purl", "Purl"))
    type = models.CharField(max_length=25, choices=pid_types)
    updated_at = models.DateTimeField("Date Updated", auto_now=True)
    policy = models.ForeignKey(Policy, blank=True, null=True)

    objects = PidManager()

    def __unicode__(self):
        return self.pid + ' ' + self.name

    def natural_key(self):
        return (self.pid,)
    
    def primary_target(self):
        '''Return the  primary target for this pid (the only target for a PURL,
        or the default target for an ARK).

        :return: :class:`Target`
        '''
        try:
            t = self.target_set.filter(qualify='')
            if len(t):
                return t[0]
        except Target.DoesNotExist:
            return None
    
    # make primary target uri easily accessible
    def primary_target_uri(self):
        target = self.primary_target()
        if target:
            return target.uri
        else:
            return ''

    # display resolvable url 
    def url(self):
        """Return the purl or ark for the primary target of this Pid.
           Returns a non-primary target url if no primary target is present."""
        target = self.primary_target()
        # if primary target is available, return ark/purl url for that target
        if target:
            return target.get_resolvable_url()
        # if non-primary targets are available, return url for one of them 
        elif len(self.target_set.all()):
            return self.target_set.all()[0].get_resolvable_url()
        # no targets
        else:
            return ''

    def url_link(self):
        """Return html for a clickable URL that opens in new window."""
        url = self.url()
        if url:
            return "<a target='_blank' href='%(url)s'>%(url)s</a>" % {'url': url}
        else:
            return ''
    url_link.short_description = "Url"
    url_link.allow_tags = True

    def primary_uri(self):
        '''Return the resolvable URL for the primary :class:`Target` associated
        with this pid.'''
        target = self.primary_target()
        if target:
            return target.get_resolvable_url()
        else:
	    return ''

    def is_valid(self):
        if (self.type == "Purl"):
            if (self.target_set.count() > 1):
                raise Exception("Purls may only have one target")
            if (self.target_set.count() and self.target_set.get().qualify != ''):
                raise Exception("Purl target may not have qualifiers")
        if (self.type == "Ark"):
            # note: this should be caught because of unique_together setting,
            # but there seems to be a bug with admin inlines
            quals = self.target_set.values_list("qualify")
            # set forces list to be unique; if length changes, qualifiers are not unique
            if len(quals) != len(set(quals)):
                raise Exception("Ark qualifiers must be unique")            
        return True

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        '''
        Custom save method to ensure that pid and noid for all associated
        :class:`Target` instances are kept in sync.
        '''
        if (self.is_valid()):
            super(Pid, self).save(force_insert=force_insert, force_update=force_update, *args, **kwargs)
            #keep pid and noid in sync
            targets = self.target_set.all()
            targets.update(noid=self.pid)

    def characters_valid(self):
        for t in self.target_set.exclude(qualify=''):
            if not valid_qualifier(t.qualify):
                return "<span style='color:red'>NO</span>"
            
        return "<span style='color:green'>Yes</span>"
    characters_valid.short_description = "Valid?"
    characters_valid.allow_tags = True

    def truncated_name(self):
        return self.name[:50]
    truncated_name.short_description = "Name"
    
    def show_target_linkcheck_status(self):
        num_passed = 0
        num_failed = 0
        num_unchecked = 0

        for t in self.target_set.all():
            try:
                if t.linkcheck_link.get().url.last_checked == None:
                    num_unchecked = num_unchecked + 1
                
                if t.linkcheck_link.get().url.status == True:
                    num_passed = num_passed + 1
                else:
                    num_failed = num_failed + 1

            except: #if target link does not exist the url was not tested
                num_unchecked = num_unchecked + 1

        total = len(self.target_set.all())

        if total == 0:
            return "<span style='font-weight: bold;'>No Targets</span>"
        elif num_unchecked > 0:
            return "<span style='font-weight: bold; color: blue;'>%(unchecked)d of %(total)d Targets Unchecked</span>" % {'unchecked': num_unchecked, 'total': total}
        elif num_failed > 0:
            return "<span style='font-weight: bold; color: red;'>%(fail)d of %(total)d Targets Fail</span>" % {'fail': num_failed, 'total': total}
        else:
            return "<span style='font-weight: bold; color: green;'>All Targets Resolve</span>"

    show_target_linkcheck_status.short_description = "Target Status"
    show_target_linkcheck_status.allow_tags = True

    def get_policy(self):
        '''Return the :class:`Policy` for this pid.  If this pid is not active,
        this method automatically returns the inactive Policy.  If the pid has
        a policy explicitly assigned, that is used; otherwise, the policy is 
        inherited from the :class:`Domain` this pid belongs to.'''
        if self.is_active() == False:
            return Policy.objects.get(title__exact='Inactive Policy')
        elif self.policy:
            return self.policy
        else:
            return self.domain.get_policy()

    def is_active(self):
        '''Determine if this Pid is active.  A Pid isconsidered active if
        **any** of its associated :class:`Target` instances are active.

        :return: boolean
        '''
        active = False
        # consider active if any targets are active
        for t in self.target_set.all():
            if t.active == True:
                active = True

        return active
    is_active.short_description = "Active ?"
    is_active.allow_tags = True
    
# proxy model & custom manager - find ARKs that have target qualifiers with invalid characters
class InvalidArkManager(PidManager):
    def get_query_set(self):
        return super(InvalidArkManager, self).get_query_set().filter(target__qualify__regex=r'[^' +
            ''.join(qualifier_allowed_characters) + ']')

class InvalidArk(Pid):
    '''Filtered set of :class:`Pid` instances that filters on invalid qualifiers.
    This model was created to make it easy to find and correct any invalid Pids
    that were added before ARK validation was added to the application.  Meant for
    access/update use only in the Django Admin interface.
    '''
    objects = InvalidArkManager()
    class Meta:
        proxy = True

class ProxyManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
class Proxy(models.Model):
    '''Use this model to define Proxy systems that should be used when resolving
    :class:`Target` instances.  The transform property is prepended to the
    target URL before resolving.
    '''
    name = models.CharField(unique=True, max_length=127)
    transform = models.CharField(max_length=127)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProxyManager()

    class Meta:
        verbose_name_plural = "Proxies"

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

class TargetManager(models.Manager):
    def get_by_natural_key(self, noid, qualifier):
        return self.get(noid=noid, qualify=qualifier)

class Target(models.Model):
    '''Target URLs associated with a :class:`Pid` instance.

    Note that each Target has the database id of the associated :class:`Pid` as
    well as the **noid**, so that resolving a Target can be done as efficiently
    as possible.
    '''
    pid = models.ForeignKey(Pid)
    noid = models.CharField(max_length=255, editable=False)
    uri = models.CharField(max_length=2048)
    qualify = models.CharField("Qualifier", max_length=255, null=False, blank=True, default='')
    proxy = models.ForeignKey(Proxy, blank=True, null=True)
    linkcheck_link = generic.GenericRelation(LinkCheckLink)
    active = models.BooleanField(default=True)

    objects = TargetManager()

    class Meta:
        unique_together = (('pid', 'qualify'))

    def __unicode__(self):
        return self.get_resolvable_url()

    def natural_key(self):
        return (self.noid, self.qualify)
    
    def get_resolvable_url(self):
        """Return the resolvable PURL or ARK URL (with any qualifiers) for this target."""
        url = settings.PID_RESOLVER_URL.rstrip('/')
        if (self.pid.type == "Purl"):
            return "/".join([url, self.noid])
        if (self.pid.type == "Ark"):
            url = "/".join([url, "ark:", settings.PID_ARK_NAAN, self.noid])
            if (self.qualify):
                url = "/".join([url, self.qualify])
            return url

    # extend default save - replace special token in target uri with noid
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        """
        Custom save method.  When present, replace a special token string
        (configured in django settings as **PID_REPLACEMENT_TOKEN**) in the
        target uri with the noid.  Also ensures that pid and noid stay
        synchronized, check that qualifier does not contain any invalid characters,
        and normalizes ARK qualifier so it will be resolved correctly.
        """
        # a special token in target URI should be replaced with minted noid
        if (self.uri.find(settings.PID_REPLACEMENT_TOKEN) != -1):
            # Note: not using self.noid because it doesn't seem to be set yet
            self.uri = self.uri.replace(settings.PID_REPLACEMENT_TOKEN, self.pid.pid)

        #keep noid and pid in sync
        if(not self.noid):
            self.noid = self.pid.pid
        elif(self.noid != self.pid.pid):
            raise ValidationError("Target.noid(%s) and Pid(%s) do not match)"%(self.noid, self.pid.pid))

        # if qualifier is not valid, it should not be saved
        if not(valid_qualifier(self.qualify)):
            raise ValidationError("Qualifier '%s' contains invalid characters"%(self.qualify))
        
        # normalize so qualifier will be found by the resolver
        self.qualify = normalize_ark(self.qualify)        
        return super(Target, self).save(force_insert=force_insert, force_update=force_update, *args, **kwargs)

    # needed by linkcheck admin
    # targets are edited from the admin view of the associated pid
    def get_admin_url(self):
        return reverse('admin:pid_pid_change', args=(self.pid_id,))

    def hit_count(self):
        return len(self.targetaccesslog_set.all())

    # needed by linkcheck admin
    def get_absolute_url(self):
        return self.get_resolvable_url()

    def linkcheck_status(self):
        lc_u = self.linkcheck_link.get().url
        return "<span style='font-size: +1; font-weight: bold; color: %(color)s;'>%(message)s</span>" % {'color':lc_u.colour, 'message':lc_u.get_message}


class TargetLinkCheck(Linklist):
    model = Target # The model this relates to
    html_fields = [] # fields in the model that contain HTML fragments
    url_fields = ['uri',] # fields in the model that contain raw url fields
    image_fields = [] # fields in the model that contain raw image fields    

def parse_resolvable_url(urlstring):
    '''Parse a PURL, ARK, or qualified ARK in resolvable url form.

    :return: dictionary with with the following keys and values:
     * type (Ark or Purl)
     * schema (http/https)
     * hostname
     * NAAN (Name authority number - ARKs only)
     * NOID
     * qualifier (qualified ARKs only)
    '''
    
    info = {"qualifier":''}     # default to '' so qualifier will always be set; override if present
    if (urlstring.find('/ark:/') != -1):
        info['type'] = "Ark"

        # NOTE: not using urlparse for ARKs because qualifier could be anything
        
        # regular expression for arks
        # 0 = scheme, 1 = server, 2 = naan, 3 = noid, 4 = qualifier
        arkpattern = re.compile('^(https?)://([a-z.]+)/ark:/([0-9]+)/([a-z0-9]+)/?(.+)?$')      
        m = arkpattern.match(urlstring)
        pieces = m.groups()
        info['scheme'] = pieces[0]
        info['hostname'] = pieces[1]
        info['naan'] = pieces[2]
        info['noid'] = pieces[3]
        if (len(pieces) > 3 and pieces[4] != None):
            info['qualifier'] = pieces[4]
    else:
        info['type'] = 'Purl'
        # purl uris are simple enough to use urlparse
        o = urlparse.urlsplit(urlstring)        
        info['scheme'] = o.scheme
        info['hostname'] = o.netloc
        info['noid'] = o.path.lstrip("/")
    return info
