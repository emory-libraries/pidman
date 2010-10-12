import os
import re
import urlparse
from denorm.fields import MirrorField
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection, models
from pidman.pidauth.models import Domain

def mint_noid():
    '''mint_noid() -> unicode
    Generate a new NOID.
    '''
    cursor = connection.cursor()
    cursor.callproc('mint_noid', [os.path.join(settings.NOID_DB_PATH, 'NOID', 'noid.bdb')])
    noid = cursor.fetchone()[0]
    cursor.close()
    return noid


class ExtSystem(models.Model):
    name = models.CharField(unique=True, max_length=127)
    key_field = models.CharField(max_length=127)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "External System"

    def __unicode__(self):
        return self.name


class Pid(models.Model):
    pid = models.CharField(unique=True, max_length=255, editable=False, default=mint_noid)
    domain = models.ForeignKey(Domain)
    active = models.BooleanField(default=True)
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

    def __unicode__(self):
        return self.pid + ' ' + self.name

    # find primary target (should be the only target for purl, default target for ark)
    def primary_target(self):
        try:
            t = self.target_set.filter(qualify='')
            if len(t):
                return t[0]
        except Target.DoesNotExist:
            return None
    
    # make primary target uri easily accessible (used in admin list view)
    def primary_target_uri(self):
        target = self.primary_target()
        if target:
            return target.uri
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
            if (len(quals) != len(set(quals))):
                raise Exception("Ark qualifiers must be unique")
        return True

    def save(self, force_insert=False, force_update=False):
        if (self.is_valid()):
            return super(Pid, self).save(force_insert=force_insert, force_update=force_update)


class Proxy(models.Model):
    name = models.CharField(unique=True, max_length=127)
    transform = models.CharField(max_length=127)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Proxies"

    def __unicode__(self):
        return self.name


class Target(models.Model):
    pid = models.ForeignKey(Pid)
    noid = MirrorField('pid', 'pid', editable=False)
    uri = models.CharField(max_length=2048)
    qualify = models.CharField("Qualifier", max_length=255, null=True, blank=True, default='')
    proxy = models.ForeignKey(Proxy, blank=True, null=True)

    class Meta:
        unique_together = (('pid', 'qualify'))

    def __unicode__(self):
        str = self.noid
        if (self.qualify):
            str += "/" + self.qualify
        str += " -> " + self.uri
        return str
    
    def get_resolvable_url(self):
        """Return the purl or ark (with any qualifiers) for this target"""
        url = settings.PID_RESOLVER_URL.rstrip('/')
        if (self.pid.type == "Purl"):
            return "/".join([url, self.noid])
        if (self.pid.type == "Ark"):
            url = "/".join([url, "ark:", settings.PID_ARK_NAAN, self.noid])
            if (self.qualify):
                url = "/".join([url, self.qualify])
            return url

    # extend default save - replace special token in target uri with noid
    def save(self, force_insert=False, force_update=False):
        # a special token in target URI should be replaced with minted noid
        if (self.uri.find(settings.PID_REPLACEMENT_TOKEN) != -1):
            # Note: not using self.noid because it doesn't seem to be set yet
            self.uri = self.uri.replace(settings.PID_REPLACEMENT_TOKEN, self.pid.pid)            
        return super(Target, self).save(force_insert=force_insert, force_update=force_update)


def parse_resolvable_url(urlstring):
    """Parse a PURL, ARK, or qualified ARK in resolvable url form"""
    
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
