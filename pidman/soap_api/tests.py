import settings
import re
import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from eulcore.soap.testclient import DjangoSoapTestServiceClient
from pidman.pid.models import Pid, Target, ExtSystem, Proxy
from pidman.pidauth.models import Domain
from pidman.soap_api.views import PersistentIdentifierService
from soaplib.serializers.primitive import Fault

class PidServiceTestCase(unittest.TestCase):
    def setUp(self):
        # test soapclient - uses django.test.client instead of http
        self.soapclient = DjangoSoapTestServiceClient('/persis_api/', PersistentIdentifierService())

        # dependent objects to use for creating test pids
        self.domain = Domain(name="test domain")
        self.domain.save()        
        self.user = User(username="soapuser")
        self.user.set_password("soappass")
        self.user.save()
        self.extsystem = ExtSystem(name="EUCLID", key_field="control_key")
        self.extsystem.save()
        self.proxy = Proxy(name="proxy1")
        self.proxy.save()

        # test ark & purl to be updated
        self.ark = Pid(name="ark to add a target to", domain=self.domain, creator=self.user,
            editor=self.user, type="Ark")
        self.ark.save()
        self.ark.target_set.create(uri="http://whee.co")
        self.purl = Pid(name="purl to update target", domain=self.domain, creator=self.user,
            editor=self.user, type="Purl")
        self.purl.save()
        self.purl.target_set.create(uri="http://tiny.url")
        

        # expected pattern for generated arks
        self.arkpattern = re.compile('^https?://[a-z.]+/ark:/[0-9]+/[a-z0-9]+(/.*)?$')
        self.purlpattern = re.compile('^https?://[a-z.]+/[a-z0-9]+$')

    def tearDown(self):
        self.domain.delete()
        self.user.delete()
        self.ark.delete()
        self.purl.delete()
        self.extsystem.delete()
        self.proxy.delete()
        
    def testGenerateArk(self):        
        ark = self.soapclient.GenerateArk("soapuser", "soappass", "http://django.com",
            "sample ark document", None, self.domain.id, None, None, None)
        # should return full, resolvable ark that was generated
        self.assert_(ark != '', "GenerateArk returns non-blank ark")        
        self.assert_(self.arkpattern.match(ark),
                     "generated ark '" + ark + "'matches expected pattern")
    
        # strip off the noid portion and inspect created ark in the db
        base_ark, slash, noid = ark.rpartition('/')
        p = Pid.objects.get(pid__exact=noid)
        self.assert_(isinstance(p, Pid), "found pid in db by noid")
        self.assertEqual("Ark", p.type)       
        self.assertEqual(self.domain.id, p.domain.id)        
        self.assert_(isinstance(p.primary_target(), Target), "found primary target")
        self.assertEqual("http://django.com", p.primary_target_uri())
        # external system & proxy not set
        self.assertEqual(None, p.ext_system)
        self.assertEqual(None, p.ext_system_key)
        self.assertEqual(None, p.primary_target().proxy)

        # generate ark with external key & proxy
        ark = self.soapclient.GenerateArk("soapuser", "soappass", "http://web.library",
            "sample ark with extsys", None, self.domain.id, self.proxy.id, "EUCLID", "ocm123")
        base_ark, slash, noid = ark.rpartition('/')
        p = Pid.objects.get(pid__exact=noid)
        self.assertEqual(self.extsystem.id, p.ext_system.id)
        self.assertEqual("ocm123", p.ext_system_key)
        self.assertEqual(self.proxy.id, p.primary_target().proxy.id)

        # generate ark with {%PID%} token in target URI
        ark = self.soapclient.GenerateArk("soapuser", "soappass", "http://web.library/" + settings.PID_REPLACEMENT_TOKEN,
            "sample ark with extsys", None, self.domain.id, None, None, None)
        self.assert_(self.arkpattern.match(ark),
                     "generated ark '" + ark + "'matches expected pattern")
        base_ark, slash, noid = ark.rpartition('/')
        p = Pid.objects.get(pid__exact=noid)
        self.assertEqual("http://web.library/" + p.pid, p.primary_target_uri())
        self.assertEqual(-1, p.primary_target_uri().find(settings.PID_REPLACEMENT_TOKEN),
                "replace token not found in target URI saved to db")

        # optional name - null should be converted to empty string
        ark = self.soapclient.GenerateArk("soapuser", "soappass", "http://django.com",
            None, None, self.domain.id, None, None, None)
        # should return full, resolvable ark that was generated        
        self.assert_(self.arkpattern.match(ark),
                     "generated ark with null name '" + ark + "'matches expected pattern")
        
        # not authenticated: legacy implementation returns soapfault with error string
        self.assertRaises(Fault,
                self.soapclient.GenerateArk, "soapuser", "badpass", "http://django.com",
                "sample ark document", None, self.domain.id, None, None, None)        
        # bad domain id
        self.assertRaises(Fault,
            self.soapclient.GenerateArk, "soapuser", "soappass", "http://django.com",
                "sample ark document", None, 3000, None, None, None)
        # bad proxy id
        self.assertRaises(Fault,
            self.soapclient.GenerateArk, "soapuser", "soappass", "http://django.com",
                "sample ark document", None, self.domain.id, 3000, None, None)
        # bad external system
        self.assertRaises(Fault,
            self.soapclient.GenerateArk, "soapuser", "soappass", "http://django.com",
                "sample ark document", None, self.domain.id, 3000, "non-existent external system", None)

    def testAddTarget(self):
        ark = self.soapclient.AddArkTarget("soapuser", "soappass", self.ark.pid,
            "qual", "http://some.url", None)
        # returns qualified ark
        self.assert_(self.arkpattern.match(ark),
                     "generated ark '" + ark + "' matches ark pattern")
        target = self.ark.target_set.filter(qualify="qual")
        self.assert_(isinstance(target[0], Target))
        self.assertEqual(1, len(target))
        self.assertEqual("http://some.url", target[0].uri)

        # not authenticated: legacy implementation returns soapfault with error string
        self.assertRaises(Fault, 
            self.soapclient.AddArkTarget, "soapuser", "badpass",
            self.ark.pid, "another_qualifier", "http://some.url", None)        

        # add a target where the qualifier already exists
        self.assertRaises(Fault,  self.soapclient.AddArkTarget, "soapuser", "soappass",
            self.ark.pid, "qual", "http://some.url", None)

        # noid not in db
        self.assertRaises(Fault, self.soapclient.AddArkTarget, "soapuser", "soappass", "bogus_noid",
            "?", "http://some.url", None)

    def testGeneratePurl(self):
        purl = self.soapclient.GeneratePurl("soapuser", "soappass", "http://pid.url",
            "sample purl document", self.domain.id, None, None, None)
        # returns purl
        self.assert_(purl != '', "GeneratePurl returns non-blank purl")
        # different pattern
        self.assert_(self.purlpattern.match(purl),
                     "generated purl '" + purl + "'matches expected pattern")

        # strip off the noid portion and inspect created ark in the db
        base_ark, slash, noid = purl.rpartition('/')
        p = Pid.objects.get(pid__exact=noid)
        self.assert_(isinstance(p, Pid), "found pid in db by noid")
        self.assertEqual("Purl", p.type)
        self.assertEqual(self.domain.id, p.domain.id)
        self.assertEqual("http://pid.url", p.primary_target_uri())

        # generate purl with external key & proxy
        purl = self.soapclient.GeneratePurl("soapuser", "soappass", "http://pid.me",
            "sample purl with extsys", self.domain.id, self.proxy.id, "EUCLID", "ocm12345")
        base_ark, slash, noid = purl.rpartition('/')
        p = Pid.objects.get(pid__exact=noid)
        self.assertEqual(self.extsystem.id, p.ext_system.id)
        self.assertEqual("ocm12345", p.ext_system_key)
        self.assertEqual(self.proxy.id, p.primary_target().proxy.id)

        # not authenticated: legacy implementation returns soapfault with error string
        self.assertRaises(Fault,
            self.soapclient.GeneratePurl, "soapuser", "badpass", "http://pid.url",
            "sample purl document", self.domain.id, None, None, None)        
        

    def testEditTarget(self):
        purl = self.soapclient.EditTarget("soapuser", "soappass",
            "http://pid.emory.edu/" + self.purl.pid, "http://new.url")
        self.assert_(self.purlpattern.match(purl),
                     "generated purl '" + purl + "'matches expected pattern")
        # get latest version from db
        p = Pid.objects.get(pk=self.purl.id)
        self.assertEqual("http://new.url", p.primary_target().uri)

        # attempting to update a non-existent purl should cause error
        self.assertRaises(Fault, self.soapclient.EditTarget, "soapuser", "soappass",
            "http://pid.emory.edu/bogus_purl", "http://new.url")

        # update an ark target
        ark = self.soapclient.EditTarget("soapuser", "soappass",
            self.ark.primary_target().get_resolvable_url(), "http://even.newer.url")
        self.assert_(self.arkpattern.match(ark),
                "generated ark '" + ark + "'matches expected pattern")
        a = Pid.objects.get(pk=self.ark.id)
        self.assertEqual("http://even.newer.url", a.primary_target().uri)

        # add then update a qualified target
        q_ark = self.soapclient.AddArkTarget("soapuser", "soappass", self.ark.pid,
                    "txt", "http://some.url", None)
        ark = self.soapclient.EditTarget("soapuser", "soappass",
            q_ark, "http://other.url")
        self.assert_(self.arkpattern.match(ark),
        	"generated ark '" + ark + "'matches expected pattern")
        target = self.ark.target_set.get(qualify="txt")
        self.assertEqual("http://other.url", target.uri)

         # not authenticated: legacy implementation returns soapfault with error string
        self.assertRaises(Fault, 
            self.soapclient.EditTarget, "soapuser", "badpass",
            self.ark.primary_target().get_resolvable_url(), "http://some.other.url")        

        # attempting to edit non-existent qualified ark target should fail        
        self.assertRaises(Fault, self.soapclient.EditTarget, "soapuser", "soappass",
            self.ark.primary_target().get_resolvable_url() + "/bad_qual", "http://new.url")

    def testWsdl(self):
        c = Client()
        resp = c.get('/persis_api/service.wsdl', **{'wsgi.url_scheme': 'http'})
        # NOTE: soaplib needs wsgi.url_scheme to be set in request environment        
        # how to check that wsdl file seems to be valid? is this even necessary/useful?
        self.assert_(resp.content != '')

