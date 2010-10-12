import unittest
from django.conf import settings
from django.test.client import Client
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpRequest, HttpResponse
from django.contrib.auth.models import User
from pidman.pid.models import Pid, Target, Domain, Proxy, Policy
from pidman.resolver.views import ark_metadata



class ResolverTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

        # dependent objects to use for creating test pids
        self.domain = Domain(name="test domain")
        self.domain.save()
        self.user = User(username="piduser")
        self.user.set_password("pidpass")
        self.user.save()
        self.policy = Policy(commitment="Not Guaranteed")
        self.policy.save()

        # test pids: one ark & one purl
        self.ark = Pid(name="testark", domain=self.domain, creator=self.user,
            editor=self.user, type="Ark", policy=self.policy)
        self.ark.save()
        self.ark.target_set.create(uri="http://some.uri")
        self.ark.target_set.create(qualify="q", uri="http://other.uri")
        self.purl = Pid(name="testpurl", domain=self.domain, creator=self.user,
            editor=self.user, type="Purl")
        self.purl.save()
        self.purl.target_set.create(uri="http://some.uri")
        self.proxy = Proxy(name="testproxy", transform="http://proxy.com?url=")
        self.proxy.save()

    def tearDown(self):
        self.domain.delete()
        self.user.delete()
        self.ark.delete()
        self.purl.delete()
        self.proxy.delete()
        self.policy.delete()

    def test_resolve_purl(self):
        response = self.client.get("/" + self.purl.pid)
        self.assert_(isinstance(response, HttpResponseRedirect), "response to resolve purl is a redirect")
        self.assertEqual(self.purl.primary_target_uri(), response["Location"])

    def test_resolve_proxied_purl(self):
        # add a proxy to the purl target
        t = self.purl.primary_target()
        t.proxy = self.proxy
        t.save()
        response = self.client.get("/" + self.purl.pid)
        self.assert_(isinstance(response, HttpResponseRedirect), "resonse to resolve purl is a redirect")
        self.assertEqual(self.proxy.transform + self.purl.primary_target_uri(), response["Location"])

    def test_resolve_ark(self):
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid)
        self.assert_(isinstance(response, HttpResponseRedirect), "response to resolver ark is a redirect")
        self.assertEqual(self.ark.primary_target_uri(), response["Location"])

    def test_resolve_inactive_ark(self):
        for t in self.ark.target_set.all():
            t.active = False
            t.save()

        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid)
        self.assertEqual(404, response.status_code)

    def test_resolve_inactive_purl(self):
        for t in self.purl.target_set.all():
            t.active = False
            t.save()

        response = self.client.get("/" + self.purl.pid)
        self.assertEqual(404, response.status_code)

    def test_resolve_qualified_ark(self):
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid + "/q")
        self.assert_(isinstance(response, HttpResponseRedirect), "response to resolve qualified ark is a redirect")
        self.assertEqual(self.ark.target_set.get(qualify='q').uri, response["Location"])

    def test_notfound_purl(self):
        response = self.client.get("/boguspurl")
        self.assert_(isinstance(response, HttpResponseNotFound), "response for non-existent purl is not found")
        self.assertEqual(404, response.status_code)

    def test_notfound_ark(self):
        response = self.client.get("/ark:/34235/bogusark")
        self.assert_(isinstance(response, HttpResponseNotFound), "response for non-existent ark is not found")
        self.assertEqual(404, response.status_code)

    def test_ark_metadata(self):
        # NOTE: can't currently test using django test client because of limitations recognizing ? with no query string
        #response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid + "?")

        request = HttpRequest()
        request.META["REQUEST_URI"] = "/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid + "?"
        response = ark_metadata(request, self.ark.pid)
        self.assert_(isinstance(response, HttpResponse), "ark_metadata returns HttpResponse")
        for header in response.items():
            if header[0] == 'Content-Type':
                self.assertEqual(header[1], "text/plain", "response has text/plain mimetype") 
        lines = response.content.splitlines()
        self.assertEqual("erc:", lines[0], "response is in ERC format")
        what = lines[1].split(":", 1)       # only split once
        self.assertEqual("what", what[0])
        self.assertEqual(self.ark.name, what[1].strip(), "ark name is listed as what:")
        where = lines[2].split(":", 1)      # only split once
        self.assertEqual("where", where[0])
        self.assertEqual(self.ark.primary_target_uri(), where[1].strip(),
			"ark target url " + self.ark.primary_target_uri() + " listed as location; got " + where[1].strip())

    def test_ark_policy(self):
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid + "??")
        self.assert_(isinstance(response, HttpResponse), "response for ark?? is an HttpResponse")
        for header in response.items():
            if header[0] == 'Content-Type':
                self.assertEqual(header[1], "text/plain", "response to ark?? is plain text");
        self.assert_("erc-support:" in response.content, "content includes 'erc-support:'")
        sections = response.content.split("erc-support:\n")
        lines = sections[1].splitlines()
        what = lines[0].split(":", 1)
        self.assertEqual("what", what[0]) 
        self.assertEqual(self.policy.commitment, what[1].strip(),
                         "what: value should be policy commitment %s, got %s" % (self.policy.commitment, what[1].strip()))
        when = lines[1].split(":", 1)
        self.assertEqual("when", when[0])
        create_date = self.policy.created_at.strftime("%Y%m%d")
        self.assertEqual(create_date, when[1].strip(), 
                         "when: value should be policy creation date " + create_date + ", got " + when[1].strip())

    def test_resolve_and_ark_normalization(self):
        # test that url rules follow ark character repertoires

        # should resolve just the same as an unqualified ark with a / or . on the end
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid + "/")
        self.assert_(isinstance(response, HttpResponseRedirect), "response for ark/ is a redirect")
        self.assertEqual(self.ark.primary_target_uri(), response["Location"],
            "redirect location for ark/ is primary target")
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid + ".")
        self.assert_(isinstance(response, HttpResponseRedirect), "response for ark. is a redirect")
        self.assertEqual(self.ark.primary_target_uri(), response["Location"],
            "redirect location for ark. is primary target")

        # hyphens in the pid should be ignored
        hyphenated_pid = '-'.join(self.ark.pid)
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + hyphenated_pid)
        self.assert_(isinstance(response, HttpResponseRedirect), "response for hyphenated pid is a redirect")
        self.assertEqual(self.ark.primary_target_uri(), response["Location"],
            "redirect location for hyphenated ark is primary target")

        # qualifier with hyphens
        target = self.ark.target_set.create(qualify="abc", uri="http://weirdos.net")
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid + '/' +
            '-'.join(target.qualify))
        self.assert_(isinstance(response, HttpResponseRedirect),
            "response for hyphenated qualifier is a redirect")
        self.assertEqual(target.uri, response["Location"], "hyphens in qualifier ignored when resolving")

        # . or / at end of qualifier should be ignored
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid +
            '/' + target.qualify + '.')
        self.assert_(isinstance(response, HttpResponseRedirect),
            "response for qualifier with following '.' is a redirect")
        self.assertEqual(target.uri, response["Location"], "'.' at end of qualifier ignored when resolving")

        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid +
            '/' + target.qualify + '/')
        self.assert_(isinstance(response, HttpResponseRedirect),
            "response for qualifier with following '/' is a redirect")
        self.assertEqual(target.uri, response["Location"], "'/' at end of qualifier ignored when resolving")

    def test_resolve_invalid_ark(self):
        # more character repertoire stuff - test allowed characters in noid & qualifier
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/123!')
        self.assert_(isinstance(response, HttpResponseNotFound),
            "response for ark with invalid characters is not found")

        # characters included in the allowed set
        self.ark.target_set.create(qualify="q=@_$", uri="http://weirdos.net")
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid + '/q=@_$')
        self.assert_(isinstance(response, HttpResponseRedirect))
        self.assertEqual("http://weirdos.net", response["Location"])

        # qualifier with invalid character
        response = self.client.get("/ark:/" + settings.PID_ARK_NAAN + '/' + self.ark.pid + '/ab^')
        self.assert_(isinstance(response, HttpResponseNotFound),
            "response for ark with invalid characters in qualifier is not found")
