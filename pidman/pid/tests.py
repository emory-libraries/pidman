import os
import re
import unittest

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

# from linkcheck.utils import find as find_links
from pidman.pid.ark_utils import normalize_ark, valid_qualifier, \
    invalid_qualifier_characters
from pidman.pid.models import Pid, Domain, Policy, Proxy, parse_resolvable_url
from pidman.pid.noid import encode_noid, decode_noid


class PidTestCase(TestCase):
    fixtures = ['pids.json']

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

    def test_mint_noid(self):
        noid = Pid.mint_noid()
        self.assertNotEqual(None, noid, "value returned by mint_noid should not be None")
        self.assert_(re.compile("^[a-z0-9]+$").match(noid),
                     "generated noid '" + noid + "' matches expected pattern")

    def test_primary_target(self):
        self.assertEqual(None, self.ark.primary_target())
        self.assertEqual(None, self.purl.primary_target())
        purl_target = self.purl.target_set.create(uri="some.uri")
        self.assertEqual(purl_target, self.purl.primary_target())
        ark_target = self.ark.target_set.create(uri="some.other.uri")
        ark_qual_target = self.ark.target_set.create(uri="some.other.uri/foo", qualify='q')
        self.assertEqual(ark_target, self.ark.primary_target())

    def test_is_valid__purl(self):
        self.assert_(self.purl.is_valid(), "purl with no targets is valid")
        self.purl.target_set.create(uri="some.uri")
        self.assert_(self.purl.is_valid(), "purl with single unqualified target is valid")
        self.purl.primary_target().qualify = "qual"
        self.assertRaises(Exception, self.purl.is_valid, "purl with single qualified target is invalid")
        self.purl.target_set.get().qualify = ""
        self.purl.target_set.create(qualify='q', uri="no.uri")
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
            t.qualify = "q"
        self.assertRaises(Exception, self.ark.is_valid, "ark with duplicate qualifiers is invalid")

    def test_purl_url(self):
        # url when there is no target
        self.assertEqual('', self.purl.url(),
            "url for purl with no target should be '', got " + self.purl.url())
        # now add a target
        self.purl.target_set.create(uri="some.uri")
        self.assertEqual(settings.PID_RESOLVER_URL + "/" + self.purl.pid, self.purl.url(),
            "url for purl with target should be " + settings.PID_RESOLVER_URL + "/" +
            self.purl.pid + ", got " + self.purl.url())

    def test_ark_url(self):
        # url when there is no target
        self.assertEqual('', self.ark.url(),
            "url for ark with no target should be '', got " + self.ark.url())
        # add a qualified target (no unqualified/primary target)
        self.ark.target_set.create(qualify="q", uri="http://ti.ny")
        self.assertEqual(settings.PID_RESOLVER_URL + "/ark:/" + settings.PID_ARK_NAAN + "/" +
            self.ark.pid + "/q", self.ark.url(), "url for ark with no primary target should be " +
            settings.PID_RESOLVER_URL + "/ark:/" + settings.PID_ARK_NAAN + "/" +
            self.ark.pid + "/q , got " + self.ark.url())
        # add an unqualified target
        self.ark.target_set.create(uri="http://wh.ee")
        self.assertEqual(settings.PID_RESOLVER_URL + "/ark:/" + settings.PID_ARK_NAAN + "/" +
            self.ark.pid, self.ark.url(), "url for ark with primary target should be " +
            settings.PID_RESOLVER_URL + "/ark:/" + settings.PID_ARK_NAAN + "/" +
            self.ark.pid + ", got " + self.ark.url())

    def test_get_policy(self):
        # pid with explicit policy set
        pid = Pid.objects.get(pk=1)
        p = pid.get_policy()
        self.assert_(isinstance(p, Policy), "Pid get_policy returns Policy object")
        self.assertEqual(p, pid.policy, "get_policy response is Pid policy")
        self.assertNotEqual(p, pid.domain.policy, "get_policy response is different than domain policy")

        # pid with no explicit policy - inherits from domain
        pid = Pid.objects.get(pk=2)
        self.assertEqual(pid.policy, None, "test pid has no explicit policy")
        p = pid.get_policy()
        self.assert_(isinstance(p, Policy), "pid get_policy returns Policy object")
        self.assertEqual(p, pid.domain.policy, "pid get_policy returns domain policy")

        # inactive pid returns inactive policy
        pid = Pid.objects.get(pk=2)
        for t in pid.target_set.all():
            t.active = False
            t.save()
        self.assertEquals(pid.is_active(), False)

        p = Policy.objects.get(title__exact='Inactive Policy')
        self.assertEquals(pid.get_policy(), p)

    def test_url_link(self):
        self.purl.target_set.create(uri="some.uri")
        url = settings.PID_RESOLVER_URL + "/" + self.purl.pid
        self.assert_(re.compile('^<a [^>]*href=[\'"]' + url + '[\'"]>' + url + '</a>$').match(self.purl.url_link()),
                     "url link for purl with target should match pattern for link with "
                     + url + ", got " + self.purl.url_link())

    def test_is_active(self):
        # setup creates ark/purl with no targets, so they are inactive
        self.assertFalse(self.ark.is_active())
        self.assertFalse(self.purl.is_active())

        purl_target = self.purl.target_set.create(uri="some.uri")
        ark_target = self.ark.target_set.create(uri="some.other.uri")
        self.assertTrue(self.ark.is_active())
        self.assertTrue(self.purl.is_active())

        purl_target.active = False
        purl_target.save()
        ark_target.active = False
        ark_target.save()

        self.assertFalse(self.ark.is_active())
        self.assertFalse(self.purl.is_active())

    def test_target_linkcheck_status(self):
        # no links checked, status -> none
        self.assertEqual(None, self.ark.target_linkcheck_status(),
            'ARK with no targets should have linkcheck status of None (unknown)')
        self.assertEqual(None, self.purl.target_linkcheck_status(),
            'PURL with no targets should have linkcheck status of None (unknown)')

        # add targets; automatically get checked and will fail
        purl_target = self.purl.target_set.create(uri="some.uri")
        ark_target = self.ark.target_set.create(uri="some.other.uri")
        ark_qual_target = self.ark.target_set.create(uri="some.other.uri/foo", qualify='q')
        self.assertFalse(self.ark.target_linkcheck_status(),
            'ARK with invalid target uris should have linkcheck status of False (error)')
        self.assertFalse(self.purl.target_linkcheck_status(),
            'PURL with invalid target uri should have linkcheck status of False (error)')

        # manually update status to check valid / mixed
        purl_linkcheck = purl_target.linkcheck.first()
        purl_linkcheck.url.status = True
        purl_linkcheck.url.save()
        self.assertTrue(self.purl.target_linkcheck_status(),
            'purl with valid target uri should have link status True (ok)')
        # one valid ark target and one invalid is still invalid
        ark_linkcheck = ark_target.linkcheck.first()
        ark_linkcheck.url.status = True
        ark_linkcheck.url.save()
        self.assertFalse(self.ark.target_linkcheck_status(),
            'ark with one valid and one invalid target uri should have ' + \
            'link status False (error)')
        ark_qual_linkcheck = ark_qual_target.linkcheck.first()
        ark_qual_linkcheck.url.status = True
        ark_qual_linkcheck.url.save()
        self.assertTrue(self.ark.target_linkcheck_status(),
            'ark with all valid target uris should have link status True (ok)')


class TargetTestCase(TestCase):
    fixtures = ['pids.json']

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

        self.proxy = Proxy(name="testproxy", transform="proxy.com?url=")
        self.proxy.save()

    def tearDown(self):
        self.domain.delete()
        self.user.delete()
        self.ark.delete()
        self.purl.delete()
        self.proxy.delete()

    def test_get_resolvable_url(self):
        t = self.ark.target_set.create(uri="some.uri")
        # test against expected ark url from settings in config file
        base_ark = settings.PID_RESOLVER_URL + "/ark:/" + settings.PID_ARK_NAAN
        self.assertEqual(base_ark + "/" + self.ark.pid, t.get_resolvable_url())
        t.qualify = ""
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

    def test_invalid_qualifier(self):
        self.assertRaises(Exception, self.ark.target_set.create,
            "attempting to save a target with invalid qualifiers raises an exception",
             qualify='q^', uri="no.uri",)

    def test_get_policy(self):
        # top-level domain
        domain = Domain.objects.get(pk=1)
        p = domain.get_policy()
        self.assert_(isinstance(p, Policy), "domain get_policy returns Policy object")
        self.assertEqual(p, domain.policy)

        #  with no explicit policy
        collection = Domain.objects.get(pk=4)
        self.assertEqual(collection.policy, None, "collection has no policy")
        p = collection.get_policy()
        self.assert_(isinstance(p, Policy), "collection get_policy returns Policy object")
        self.assertEqual(p, collection.parent.policy, "collection get_policy returns parent domain's policy")

        # collection with explicit policy different from parent domain
        collection = Domain.objects.get(pk=2)
        self.assert_(isinstance(collection.policy, Policy), "collection has its own policy")
        p = collection.get_policy()
        self.assert_(isinstance(p, Policy), "collection get_policy returns Policy object")
        self.assertEqual(p, collection.policy, "collection get_policy returns collection's policy")
        self.assertNotEqual(p, collection.parent.policy, "collection get_policy returns collection's policy")

class ParseResolvableUrlTestCase(TestCase):
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

class ArkUtilsTestCase(TestCase):

    def test_normalize_ark(self):
        # examples here are from the character repertoires section of ARK spec
        n = normalize_ark("65-4-xz-321")
        self.assertEqual("654xz321", n,
            "65-4-xz-321 should be normalized to 654xz321, got '" + n + "'")
        n = normalize_ark("654--xz32-1")
        self.assertEqual("654xz321", n,
            "654--xz32-1 should be normalized to 654xz321, got '" + n + "'")
        n = normalize_ark("654xz321")
        self.assertEqual("654xz321", n,
            "654xz321 should be normalized to 654xz321, got '" + n + "'")

        # remove / or . as last char
        n = normalize_ark("654.")
        self.assertEqual("654", n, "654. should be normalized to 654, got '" + n + "'")
        n = normalize_ark("654/")
        self.assertEqual("654", n, "654/ should be normalized to 654, got '" + n + "'")
        n = normalize_ark("6-5-4.")
        self.assertEqual("654", n, "6-5-4. should be normalized to 654, got '" + n +"'")

    def test_valid_qualifier(self):
        self.assertTrue(valid_qualifier("45ae%"), "'45ae%' is a valid qualifier")
        self.assertFalse(valid_qualifier("45ae^"), "'45ae^' is not a valid qualifier")

    def test_invalid_qualifier_characters(self):
        self.assertEqual(['^'], invalid_qualifier_characters('45ae^'))
        self.assertEqual(['^', '~'], invalid_qualifier_characters('45ae^0u~f'))
        self.assertEqual(['^~', ':;'], invalid_qualifier_characters('ab^~cde:;f'))


class NoidTestCase(TestCase):
    def test_round_trip_to_int(self):
        for i in xrange(10000):
            pid = encode_noid(i)
            decoded = decode_noid(pid)
            self.assertEqual(i, decoded)

    def test_encode_known_pids(self):
        # check codec logic against a sample of real production noids
        noids = ['2dbx', '5z8x', '13kpr', '17gvd', '17ktk']
        for noid in noids:
            i = decode_noid(noid)
            encoded = encode_noid(i)
            self.assertEqual(noid, encoded)
