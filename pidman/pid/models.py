import os
import re
import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.db import connection, models, transaction

from mptt.models import MPTTModel, TreeForeignKey
from sequences import get_next_value
from linkcheck.models import Link

from pidman.pid.ark_utils import normalize_ark, valid_qualifier, qualifier_allowed_characters
from pidman.pid.noid import encode_noid, decode_noid
from django.core.exceptions import ValidationError


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
    title = models.CharField(unique=True, max_length=255)

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

class Domain(MPTTModel):
    '''A Domain is a collection of :class:`Pid` instances.  Domains can have an
    associated :class:`Policy`, which all Pids in that collection inherit by
    default.  This implementation allows for collections or subdomains
    that belong to a domain (currently only supports one level of nesting).

    Domains are **not** part of the ARK spec, but a feature of this implementation
    meant for managing and grouping PIDs.
    '''
    name = models.CharField(unique=True, max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    policy = models.ForeignKey(Policy, blank=True, null=True,
        help_text='Policy statement for pids in this domain')
    parent = TreeForeignKey('self', blank=True, null=True,
                related_name='collections', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Domain %s>' % unicode(self)

    def get_policy(self):
        '''Return the policy for this domain or from parent domain if inherited.
        Raises a :class:`DomainException` if no policy is found.

        :return: instance of :class:`Policy`
        '''
        if self.policy:
            return self.policy
        elif self.parent:
            # traverse the hierarchy, closest ancestor first,
            # and find the first one with a policy
            return self.get_ancestors(ascending=True).filter(policy__isnull=False).first().policy
        else:
            raise DomainException("No Policy Exists")

    def show_policy(self):
        try:
            return self.get_policy()
        except DomainException:
            return '(no policy set)'
    show_policy.short_description = 'Policy'

    def subdomain_count(self):
        return self.get_descendant_count()
    subdomain_count.short_description = '# collections'

    def num_pids(self):
        '''Number of :class:`Pid` instances in this domain, including those in
        any subdomains.'''
        domain_ids = self.get_descendants(include_self=True).values_list('id', flat=True)
        return Pid.objects.filter(domain__in=domain_ids).count()
    num_pids.short_description = "# pids"

class PidManager(models.Manager):
    def get_by_natural_key(self, noid):
        return self.get(pid=noid)

class Pid(models.Model):
    '''Pid: an ARK or a PURL, with associated :class:`Target` instance(s).'''
    pid = models.CharField(unique=True, max_length=255, editable=False)
    # NOTE: previously, pid value was set using a default=mint_noid;
    # now, to use sequence cleanly, noid is only Cleanset when saving a new Pid
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

    SEQUENCE_NAME = 'pid_noid'

    objects = PidManager()

    def __unicode__(self):
        return self.pid + ' ' + self.name

    def natural_key(self):
        return (self.pid,)

    @classmethod
    def next_sequence_value(cls):
        return get_next_value(cls.SEQUENCE_NAME)

    @classmethod
    def mint_noid(cls):
        '''Generate a new NOID (Nice Opaque IDentifier).'''
        return encode_noid(cls.next_sequence_value())

    def primary_target(self):
        '''Return the  primary target for this pid (the only target for a PURL,
        or the default target for an ARK).

        :return: :class:`Target`
        '''
        # NOTE: this method is used in django-admin change list;
        # intentionally does not hit the database, since it requires
        # one query per pid
        for target in self.target_set.all():
            if target.qualify == '':
                return target
        return None

    # make primary target uri easily accessible
    def primary_target_uri(self):
        '''Return the resolvable URL for the primary :class:`Target` associated
        with this pid.'''
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
    url_link.short_description = "URL"
    url_link.allow_tags = True

    def is_valid(self):
        if self.type == "Purl":
            if self.target_set.count() > 1:
                raise Exception("Purls may only have one target")
            if self.target_set.count() and self.target_set.get().qualify != '':
                raise Exception("Purl target may not have qualifiers")
        if self.type == "Ark":
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
        # don't save invalid records
        # NOTE: should this add logging or an exception, instead of failing silently?
        if self.is_valid():
            # if primary key is not set, we are saving a new pid
            # - mint a new noid based in our pid sequence
            if self.pk is None:
                with transaction.atomic():
                    self.pid = Pid.mint_noid()
                    super(Pid, self).save(force_insert=force_insert,
                         force_update=force_update, *args, **kwargs)
            else:
                super(Pid, self).save(force_insert=force_insert,
                     force_update=force_update, *args, **kwargs)

            # keep pid and noid in sync
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
        '''Determine if this Pid is active.  A Pid is considered active if
        **any** of its associated :class:`Target` instances are active.

        :return: boolean
        '''
        # consider active if any targets are active
        return any([target.active for target in self.target_set.all()])
    is_active.short_description = "Active ?"
    is_active.allow_tags = True
    is_active.boolean = True

    def target_linkcheck_status(self):
        '''Determine summary linkcheck status for target(s) associated
        with this pid.  Return values:

            - None : unknown or unchecked; returns None if any associated
              targets have not been checked *or* if the Pid has
              no associated targets
            - True: all target URIs have been checked and are ok
            - False: any target URIs have been checked and errored
        '''
        # true - all ok
        # false - any not ok
        # none - any unknown / unchecked

        # if a pid has no targets, consider it unchecked
        if not self.target_set.exists():
            return None

        # get all linkcheck status for all target urls
        # linkcheck status is true for ok, false for error

        # NOTE: iterating here to take advantage of pre-fetching
        # results as configured for admin change list
        linkcheck = []
        for target in self.target_set.all():
            linkcheck.extend(target.linkcheck.all())
        if not linkcheck:
            return None
        link_status = [link.url.status for link in linkcheck]

        # if the number of statuses doesn't match the number of targets,
        # then return None for unknown/unchecked
        if self.target_set.all().count() != len(link_status):
            return None
        else:
            # ok if all are true, otherwise there are some errors
            return all(link_status)

    def linkcheck_status(self):
        # move to target for reuse?
        link_status = None
        if self.target_set.exists():
            link_status = self.target_linkcheck_status()
            if link_status is None:
                status = LINKCHECK_STATUS['unknown']
            elif link_status:
                status = LINKCHECK_STATUS['ok']
            else:
                status = LINKCHECK_STATUS['alert']
        else:
            status = LINKCHECK_STATUS['no_urls']

        tag = '<i style="color:%(color)s" class="fa fa-%(icon)s" title="%(title)s"></i>' \
            % status
        if 'filter' in status:
            tag = '<a href="%s?filters=%s">%s</a>' % \
                (reverse('linkcheck:linkcheck_report'), status['filter'], tag)
        return tag
    linkcheck_status.short_description = 'URL Status'
    linkcheck_status.allow_tags = True


LINKCHECK_STATUS = {
    'no_urls': {'color': 'black', 'icon': 'ban', 'title': 'No URLs'},
    'ok': {'color': 'green', 'icon': 'check', 'title': 'All URLs ok',
            'filter': 'show_valid'},
    'alert': {'color': 'red', 'icon': 'exclamation-triangle', 'title': 'Some errors',
            'filter': 'show_invalid'},
    'unknown': {'color': 'blue', 'icon': 'question-circle', 'title': 'Unchecked',
            'filter': 'show_unchecked'},
}

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
    # NOTE: previously uri was a charfield, because URLField was only
    # introduced in Django 1.5.
    uri = models.URLField(max_length=2048)
    qualify = models.CharField("Qualifier", max_length=255, null=False, blank=True, default='')
    proxy = models.ForeignKey(Proxy, blank=True, null=True)
    active = models.BooleanField(default=True)

    linkcheck = GenericRelation(Link)

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

    # def link_status(self):



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
