import unittest
from django.conf import settings
from django.contrib.auth.models import User
from pidman.pid.models import Pid, Target, Domain, parse_resolvable_url


class PidTestCase(unittest.TestCase):
    def setUp(self):
        # dependent objects to use for creating test pids
        self.domain = Domain(name="test domain")
        self.domain.save()
        self.user = User(username="piduser")
        self.user.set_password("pidpass")
        self.user.save()
        
        # test pids: one ark & one purl
        self.ark = Pid(name="testark", domain=self.domain, creator=self.user,
            editor=self.user, type="Ark")
        self.ark.save()        
        self.purl = Pid(name="testpurl", domain=self.domain, creator=self.user,
            editor=self.user, type="Purl")
        self.purl.save()        

    def tearDown(self):
        self.domain.delete()
        self.user.delete()
        self.ark.delete()
        self.purl.delete()        

    def test_is_valid__purl(self):        
        self.assert_(self.purl.is_valid(), "purl with no targets is valid")
        self.purl.target_set.create(uri="some.uri")
        self.assert_(self.purl.is_valid(), "purl with single unqualified target is valid")
        self.purl.primary_target().qualify = "qual"        
        self.assertRaises(Exception, self.purl.is_valid, "purl with single qualified target is invalid")
        self.purl.target_set.get().qualify = ""
        self.purl.target_set.create(qualify='q',uri="no.uri")
        self.assertRaises(Exception, self.purl.is_valid, "purl with multiple targets is invalid")

    def test_is_valid__ark(self):
        self.assert_(self.ark.is_valid(), "ark with no targets is valid")
        self.ark.target_set.create(uri="http://some.uri")
        self.assert_(self.ark.is_valid(), "ark with one unqualified target is valid")
        self.ark.target_set.create(qualify="q", uri="http://other.uri")
        self.assert_(self.ark.is_valid(), "ark with two targets is valid")

        self.ark.target_set.create(qualify="qual", uri="http://some.url", proxy=None)
        self.assert_(self.ark.is_valid(), "ark with two targets is valid")

        for t in self.ark.target_set.all():
            t.qualify="q"
        self.assertRaises(Exception, self.ark.is_valid, "ark with duplicate qualifiers is invalid")

        


class TargetTestCase(unittest.TestCase):
    def setUp(self):
        # dependent objects to use for creating test pids
        self.domain = Domain(name="test domain")
        self.domain.save()
        self.user = User(username="piduser")
        self.user.set_password("pidpass")
        self.user.save()

        self.ark = Pid(name="testark", domain=self.domain, creator=self.user,
            editor=self.user, type="Ark")
        self.ark.save()
        self.purl = Pid(name="testpurl", domain=self.domain, creator=self.user,
            editor=self.user, type="Purl")
        self.purl.save()

    def tearDown(self):
        self.domain.delete()
        self.user.delete()
        self.ark.delete()
        self.purl.delete()

    def test_get_resolvable_url(self):        
        t = self.ark.target_set.create(uri="some.uri")
        # test against expected ark url from settings in config file
        base_ark = settings.PID_RESOLVER_URL + "/ark:/" + settings.PID_ARK_NAAN
        self.assertEqual(base_ark + "/" + self.ark.pid, t.get_resolvable_url())
        t.qualify=None
        self.assertEqual(base_ark + "/" + self.ark.pid, t.get_resolvable_url())
        t.qualify = "?"
        self.assertEqual(base_ark + "/" + self.ark.pid + "/?", t.get_resolvable_url())
        t.qualify = "some/long/qualifier.txt"
        self.assertEqual(base_ark + "/" + self.ark.pid + "/some/long/qualifier.txt", t.get_resolvable_url())

        
        t = self.purl.target_set.create(uri="some.uri")
        self.assertEqual(settings.PID_RESOLVER_URL + "/" + self.purl.pid, t.get_resolvable_url())

    def test_token_replacement(self):        
        self.ark.target_set.create(uri="http://some.url/with/" + settings.PID_REPLACEMENT_TOKEN)
        self.assertEqual("http://some.url/with/" + self.ark.pid, self.ark.primary_target().uri)

class parse_resolvable_urlTestCase(unittest.TestCase):
    def test_parse_resolvable_url(self):
        # simple purl
        p = parse_resolvable_url("http://pid.emory.edu/123")
        self.assertEqual("http", p['scheme'])
        self.assertEqual("pid.emory.edu", p['hostname'])
        self.assertEqual("Purl", p['type'])
        self.assertEqual("123", p['noid'])
        # unqualified ark
        p = parse_resolvable_url("https://pidtest.com/ark:/909/23a")
        self.assertEqual("https", p['scheme'])
        self.assertEqual("pidtest.com", p['hostname'])
        self.assertEqual("Ark", p['type'])
        self.assertEqual("909", p['naan'])
        self.assertEqual("23a", p['noid'])
        self.assertEqual('', p['qualifier'])
        # qualified arks
        p = parse_resolvable_url("http://pidtest.com/ark:/909/23a/PDF")
        self.assertEqual("PDF", p['qualifier'])

        p = parse_resolvable_url("http://pidtest.com/ark:/5439/d00d/some/long/qualifier.txt")
        self.assertEqual("Ark", p['type'])
        self.assertEqual("5439", p['naan'])
        self.assertEqual("d00d", p['noid'])
        self.assertEqual("some/long/qualifier.txt", p['qualifier'])

        # special case qualifiers - not yet handled, but would like to be able to recognize
        p = parse_resolvable_url("http://pidtest.com/ark:/909/23a?")
        self.assertEqual("?", p['qualifier'])
        p = parse_resolvable_url("http://pidtest.com/ark:/909/23a??")
        self.assertEqual("??", p['qualifier'])

