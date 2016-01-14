from base64 import b64encode
import json
import re
import urllib

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import Client
from django.test import TransactionTestCase
from django.utils.encoding import force_unicode
from pidman.pid.models import Domain
from pidman.pid.models import Pid
from pidman.rest_api.views import domain_data
from pidman.rest_api.views import pid_data
from pidman.rest_api.views import target_data, _domain_from_uri

# NOTE: developers using Firefox may find it helpful to install the JSONView plugin

user_credentials = ('testuser', 'norestforthewicked')
admin_credentials = ('testadmin', 'restmaster')

def auth_header(username, password):
    token = b64encode('%s:%s' % (username, password))
    return {'HTTP_AUTHORIZATION': 'Basic ' + token}

ADMIN_AUTH = auth_header(*admin_credentials)

# Note using TransactionTestCase here because some test / functions depend on the ability to rollback the transaction
# See http://docs.djangoproject.com/en/1.2/topics/testing/#django.test.TransactionTestCase
class RestApiTestCase(TransactionTestCase):
    fixtures = ['rest_pids.json']

    # info about fixture data
    purl_pid = '8g1wx'
    inactive_purl_pid = '124tw'
    ark_pid = '8crx1'
    ark_qual = 'PDF'

    # regex for isoformat dates
    isodate_re = re.compile('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(.\d{6}|[+-]\d{2}:\d{2})?$')
    noid_pattern = '[a-z0-9]+'  # very simplified noid regex
    purl_regex = re.compile('^%s/%s$' % (settings.PID_RESOLVER_URL, noid_pattern))
    ark_regex = re.compile('^%s/ark:/%s/%s(/.*)$' % (settings.PID_RESOLVER_URL,
                                              settings.PID_ARK_NAAN, noid_pattern))

    def setUp(self):
        self.client = Client()

        # retrieve references to test objects
        self.ark = Pid.objects.get(pid=self.ark_pid)
        self.purl = Pid.objects.get(pid=self.purl_pid)
        self.inactive_purl = Pid.objects.get(pid=self.inactive_purl_pid)

        self.request = HttpRequest()
        self.request.META['SERVER_NAME'] = 'pid.org'
        self.request.META['SERVER_PORT'] = 80

    def assertLogEntryForObject(self, obj):
        # Asserts a log entry entered for a given object.  Very generic on
        # on purpose.
        ct = ContentType.objects.get_for_model(obj)
        log_entry = LogEntry.objects.get(content_type=ct, object_id=obj.pk)
        self.assertTrue(log_entry, "Log entry for action on %s not found!" % force_unicode(obj))

    def test_get_purl(self):
        # purl
        purl_url = reverse('rest_api:pid', kwargs={'noid': self.purl.pid, 'type': 'purl'})
        response = self.client.get(purl_url)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got, "Expected status code %s for %s, got %s" \
                % (expected, purl_url, got))
        expected, got = 'application/json', response['Content-Type']
        self.assertEqual(expected, got, "Expected Content-Type '%s' for GET on %s, got '%s'" \
            % (expected, purl_url, got))
        data = json.loads(response.content)
        self.assert_(data, "Response content successfully loaded as JSON")
        self.assert_(data['uri'].endswith(purl_url),
                    "PURL resource URI present in response")

        # bogus purl - 404
        purl_url = reverse('rest_api:pid', kwargs={'noid': 'bogus','type': 'purl'})
        response = self.client.get(purl_url)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got, "Expected status code %s for %s (bogus id), got %s" \
                % (expected, purl_url, got))

        # valid purl as ark - 404
        purl_url = reverse('rest_api:pid', kwargs={'noid': self.purl.pid, 'type': 'ark'})
        response = self.client.get(purl_url)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s for %s (purl id with type 'ark'), got %s" \
                % (expected, purl_url, got))

    def test_get_purl_target(self):
        # purl target
        purl_url = reverse('rest_api:pid', kwargs={'noid': self.purl.pid, 'type': 'purl'})
        target_url = reverse('rest_api:purl-target', kwargs={'noid': self.purl.pid})
        response = self.client.get(target_url)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got, "Expected status code %s for %s, got %s" \
                % (expected, target_url, got))
        data = json.loads(response.content)
        self.assert_(data, "Response content successfully loaded as JSON")
        self.assert_(data['uri'].endswith(target_url),
                    "PURL target resource URI present in response")
        self.assert_(data['pid'].endswith(purl_url),
                    "PURL resource URI present in response")

        # valid purl target as ark target - 404
        target_url = reverse('rest_api:ark-target', kwargs={'noid': self.purl.pid,
                'qualifier': ''})
        response = self.client.get(target_url)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s for %s (purl target with type 'ark'), got %s" \
                % (expected, target_url, got))

    def test_get_ark(self):
        # ark
        ark_url = reverse('rest_api:pid', kwargs={'noid': self.ark.pid, 'type': 'ark'})
        response = self.client.get(ark_url)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got, "Expected status code %s for %s, got %s" \
                % (expected, ark_url, got))
        expected, got = 'application/json', response['Content-Type']
        self.assertEqual(expected, got, "Expected Content-Type '%s' for GET on %s, got '%s'" \
            % (expected, ark_url, got))
        data = json.loads(response.content)
        self.assert_(data, "Response content successfully loaded as JSON")
        self.assert_(data['uri'].endswith(ark_url),
                    "ARK resource URI present in response")

        # bogus ark - 404
        ark_url = reverse('rest_api:pid', kwargs={'noid': 'bogus','type': 'ark'})
        response = self.client.get(ark_url)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got, "Expected status code %s for %s (bogus id), got %s" \
                % (expected, ark_url, got))

        # valid ark as purl - 404
        ark_url = reverse('rest_api:pid', kwargs={'noid': self.ark.pid, 'type': 'purl'})
        response = self.client.get(ark_url)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s for %s (ark id with type 'purl'), got %s" \
                % (expected, ark_url, got))

    def test_get_ark_target(self):
        # unqualified ark target
        ark_url = reverse('rest_api:pid', kwargs={'noid': self.ark.pid,
                                                  'type': 'ark'})
        target_url = reverse('rest_api:ark-target', kwargs={'noid': self.ark.pid,
                'qualifier': ''})
        response = self.client.get(target_url)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s for unqualified ark target %s, got %s" \
                % (expected, target_url, got))
        data = json.loads(response.content)
        self.assert_(data, "Response content successfully loaded as JSON")
        self.assert_(data['uri'].endswith(target_url),
                    "ARK target resource URI present in response")
        self.assert_(data['pid'].endswith(ark_url),
                    "ARK resource URI present in response")

        # qualified ark target
        target_url = reverse('rest_api:ark-target', kwargs={'noid': self.ark.pid,
                'qualifier': self.ark_qual})
        response = self.client.get(target_url)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s for qualified ark target %s, got %s" \
                % (expected, target_url, got))
        data = json.loads(response.content)
        self.assert_(data, "Response content successfully loaded as JSON")
        self.assert_(data['uri'].endswith(target_url),
                    "ARK target resource URI present in response")
        self.assert_(data['pid'].endswith(ark_url),
                    "ARK resource URI present in response")

        # nonexistent qualifier - 404
        target_url = reverse('rest_api:ark-target', kwargs={'noid': self.ark.pid,
                'qualifier': 'bogus'})
        response = self.client.get(target_url)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s for %s (nonexistent qualifier), got %s" \
                % (expected, target_url, got))

         # valid ark target as purl target - 404
        target_url = reverse('rest_api:purl-target', kwargs={'noid': self.ark.pid})
        response = self.client.get(target_url)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s for %s (purl target with type 'ark'), got %s" \
                % (expected, target_url, got))


    def test_create_purl(self):
        create_purl = reverse('rest_api:create-pid', kwargs={'type': 'purl'})

        # create a purl with bare minimum data options: domain + target
        domain_id = 1
        domain_uri = 'http://testserver' + reverse('rest_api:domain',
                                                kwargs={'id': domain_id})
        purl_data = {
            'domain': domain_uri,
            'target_uri': 'http://my.new.purl/target'
        }
        response = self.client.post(create_purl, purl_data, **ADMIN_AUTH)
        expected, got = 201, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (created) for POST to %s, got %s" \
                % (expected, create_purl, got))
        self.assert_(self.purl_regex.match(response.content),
                "content response is a PURL - %s should match regular expression %s" %\
                (response.content, self.purl_regex.pattern))
        # retrieve pid from db and inspect the objects created
        noid = response.content.split('/')[-1]
        pid = Pid.objects.get(pid=noid)
        self.assertEqual(pid.type, 'Purl', 'new pid created as type Purl')
        self.assertEqual(domain_id, pid.domain.id,
            'Pid domain set correctly from domain URI in POST; expected %s, got %s' \
            % (domain_id, pid.domain.id))
        self.assertEqual(purl_data['target_uri'], pid.primary_target_uri(),
            'Primary target URI set from POST data; expected %s, got %s' \
            % (purl_data['target_uri'], pid.primary_target_uri()))
        self.assertEqual('testadmin', pid.creator.username,
            'Authenticated user is set as pid creator')
        self.assertEqual('testadmin', pid.editor.username,
            'Authenticated user is set as pid editor')

        # Test that log entry was created
        self.assertLogEntryForObject(pid)
        # Assert log for target creation as well.
        self.assertLogEntryForObject(pid.target_set.all()[0])

        # create a purl with all possible data options specified
        # - name, proxy, external system, policy
        purl_data.update({
            'name': 'my new purl',
            'external_system_id': 'EUCLID',
            'external_system_key': 'ocn49128',
            'policy': 'Not Guaranteed',
            'proxy': 'EZproxy'
        })
        response = self.client.post(create_purl, purl_data, **ADMIN_AUTH)
        expected, got = 201, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (created) for POST to %s, got %s" \
                % (expected, create_purl, got))
        # retrieve pid from db and inspect the objects created
        noid = response.content.split('/')[-1]
        pid = Pid.objects.get(pid=noid)
        self.assertEqual(purl_data['name'], pid.name,
            'Pid name set correctly from POSTed data; expected %s, got %s' \
            % (purl_data['name'], pid.name))
        self.assertEqual(purl_data['external_system_id'], pid.ext_system.name,
            'Pid external system set correctly from POSTed data; expected %s, got %s' \
            % (purl_data['external_system_id'], pid.ext_system.name))
        self.assertEqual(purl_data['external_system_key'], pid.ext_system_key,
            'Pid external system key set correctly from POSTed data; expected %s, got %s' \
            % (purl_data['external_system_key'], pid.ext_system_key))
        self.assertEqual(purl_data['policy'], pid.policy.title,
            'Pid policy set correctly from POSTed data; expected %s, got %s' \
            % (purl_data['policy'], pid.policy.title))
        self.assertEqual(purl_data['proxy'], pid.primary_target().proxy.name,
            'Proxy set correctly on pid target from POSTed data; expected %s, got %s' \
            % (purl_data['proxy'], pid.primary_target().proxy.name))

        # Test that logging was done properly
        self.assertLogEntryForObject(pid)
        # Assert log for target creation as well.
        self.assertLogEntryForObject(pid.target_set.all()[0])

        # test for required fields not present in POSTed data
        #   - no domain
        response = self.client.post(create_purl, {'target_uri': 'foo'}, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for missing domain to %s, got %s" \
                % (expected, create_purl, got))
        self.assertContains(response, 'Error: domain and target_uri are required',
                status_code=400, msg_prefix='Response indicates required fields missing')
        #   - no target
        response = self.client.post(create_purl, {'domain': domain_uri}, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for missing target URI to %s, got %s" \
                % (expected, create_purl, got))
        #   - no args
        response = self.client.post(create_purl, {}, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for no data to %s, got %s" \
                % (expected, create_purl, got))

        # bad domain
        #  - not parseable as a url
        response = self.client.post(create_purl, {'target_uri': 'foo',
                                                  'domain': 'bar'}, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for non-url domain URI to %s, got %s" \
                % (expected, create_purl, got))
        self.assertContains(response, 'Error: Could not resolve domain URI',
                status_code=400, msg_prefix='Response indicates domain URI resolve error')
        # valid url but not a domain URI
        non_domain_uri = 'http://bar.com/'
        response = self.client.post(create_purl, {'target_uri': 'foo',
                                    'domain': non_domain_uri}, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for non-domain URI to %s, got %s" \
                % (expected, create_purl, got))
        # self.assertContains(response, 'Error: Could not resolve domain URI %s' % non_domain_uri,
        self.assertContains(response, 'Error: Could not resolve domain URI into a domain',
                status_code=400, msg_prefix='Response indicates domain URI resolve error')
        # - invalid domain id
        domain_uri = 'http://testserver' + reverse('rest_api:domain', kwargs={'id': 3023})
        response = self.client.post(create_purl, {'target_uri': 'foo',
                                                  'domain': domain_uri}, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for non-existent domain id to %s, got %s" \
                % (expected, create_purl, got))
        self.assertContains(response, 'Error: Could not find Domain for URI %s' % domain_uri,
                status_code=400, msg_prefix='Response indicates domain does not exist')

        # invalid ids for other related objects
        #  - external system
        data = purl_data.copy()
        data['external_system_id'] =  'BOGUS'
        response = self.client.post(create_purl, data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for bogus external system id to %s, got %s" \
                % (expected, create_purl, got))
        self.assertContains(response, "Error: External System 'BOGUS' not found",
                status_code=400, msg_prefix='Response indicates external system does not exist')
        # - policy
        data = purl_data.copy()
        data['policy'] =  'No Access'
        response = self.client.post(create_purl, data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for bogus policy to %s, got %s" \
                % (expected, create_purl, got))
        self.assertContains(response, "Error: Policy 'No Access' not found",
                status_code=400, msg_prefix='Response indicates policy does not exist')
        # - proxy
        data = purl_data.copy()
        data['proxy'] =  'ToughProxy'
        response = self.client.post(create_purl, data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for bogus proxy to %s, got %s" \
                % (expected, create_purl, got))
        self.assertContains(response, "Error: Proxy 'ToughProxy' not found",
                status_code=400, msg_prefix='Response indicates proxy does not exist')

        # invalid combination - purl + qualifier
        purl_data['qualifier'] = 'test'
        response = self.client.post(create_purl, purl_data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for purl with qualifier to %s, got %s" \
                % (expected, create_purl, got))
        self.assertContains(response, "Error: Purl targets can not have qualifiers",
                status_code=400, msg_prefix='Response indicates purl+qualifier error')


    def test_create_ark(self):
        create_ark = reverse('rest_api:create-pid', kwargs={'type': 'ark'})
        # create a purl with bare minimum data options: domain + target
        domain_id = 1
        domain_uri = 'http://testserver' + reverse('rest_api:domain',
                                                kwargs={'id': domain_id})
        pid_data = {
            'domain': domain_uri,
            'target_uri': 'http://my.new.purl/target',
            'qualifier': 'X'
        }
        response = self.client.post(create_ark, pid_data, **ADMIN_AUTH)
        expected, got = 201, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (created) for POST to %s, got %s" \
                % (expected, create_ark, got))
        self.assert_(self.ark_regex.match(response.content),
                "content response is an ARK - %s should match regular expression %s" %\
                (response.content, self.ark_regex.pattern))
        # retrieve pid from db and inspect the objects created
        noid = response.content.split('/')[-2]      # requested qualified ARK
        pid = Pid.objects.get(pid=noid)
        self.assertEqual(pid.type, 'Ark', 'new pid created as type Ark')
        self.assertEqual(pid_data['qualifier'], pid.target_set.all()[0].qualify,
            'ARK target created with requested target; expected %s, got %s' \
            % (pid_data['qualifier'], pid.target_set.all()[0].qualify))

        # Test that logging was done properly
        self.assertLogEntryForObject(pid)
        # Assert log for target creation as well.
        self.assertLogEntryForObject(pid.target_set.all()[0])

        # invalid qualifier
        pid_data['qualifier'] = '!'
        response = self.client.post(create_ark, pid_data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for invalid qualifier to %s, got %s" \
                % (expected, create_ark, got))
        self.assertContains(response, "Error: Qualifier '!' contains invalid characters",
                status_code=400, msg_prefix='Response indicates qualifier is invalid')

    def test_create_pid_permissions(self):
        create_pid = reverse('rest_api:create-pid', kwargs={'type': 'purl'})
        # test authorization

        # - no credentials
        response = self.client.post(create_pid, {})
        expected, got = 401, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (unauthorized) for %s with no credentials, got %s" \
                % (expected, create_pid, got))

        # - invalid credentials
        AUTH = auth_header('testuser', 'notmypassword')
        response = self.client.post(create_pid, {}, **AUTH)
        expected, got = 401, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (unauthorized) for %s with no credentials, got %s" \
                % (expected, create_pid, got))

        # - valid credentials but user doesn't have required permissions
        AUTH = auth_header(*user_credentials)
        response = self.client.post(create_pid, {}, **AUTH)
        expected, got = 403, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (forbidden) for %s as valid user with insufficent permissions, got %s" \
                % (expected, create_pid, got))

    def test_update_pid(self):
        purl_uri = reverse('rest_api:pid', kwargs={'noid': self.purl.pid, 'type': 'purl'})

        domain_id = 1
        domain_uri = 'http://testserver' + reverse('rest_api:domain',
                                                kwargs={'id': domain_id})
        new = {
            'domain': domain_uri,
            'name': 'totally new name',
            'external_system_id': 'EUCLID',
            'external_system_key': 'ocm34123979',
            'policy': 'Not Guaranteed'
        }
        response = self.client.put(purl_uri, json.dumps(new),
                                   content_type='application/json', **ADMIN_AUTH)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (Ok) for PUT on %s , got %s" \
                % (expected, purl_uri, got))
        # should return updated pid info
        expected, got = 'application/json', response['Content-Type']
        self.assertEqual(expected, got, "Expected Content-Type '%s' for PUT on %s, got '%s'" \
            % (expected, purl_uri, got))
        data = json.loads(response.content)
        self.assert_(data, "Response content successfully loaded as JSON")
        self.assert_(data['uri'].endswith(purl_uri),
                    "PURL resource URI present in response")

        # inspect updated object in db
        purl = Pid.objects.get(pid=self.purl_pid)
        self.assertEqual(new['name'], purl.name)
        self.assertEqual(new['external_system_id'], purl.ext_system.name)
        self.assertEqual(new['external_system_key'], purl.ext_system_key)
        self.assertEqual(domain_id, purl.domain.id)
        self.assertEqual(new['policy'], purl.policy.title)
        self.assertEqual('testadmin', purl.editor.username,
                        'Authenticated user is set as  pid editor')

        # Test that log entry was created
        self.assertLogEntryForObject(purl)

        # test PUTing non-JSON content
        response = self.client.put(purl_uri, 'bogus pid data',
                                   content_type='text/plain', **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (bad request) for PUT with unsupported content type on %s, got %s" \
                % (expected, purl_uri, got))
        self.assertContains(response, 'Unsupported content type', status_code=400)

        # invalid pid should 404
        purl_uri = reverse('rest_api:pid', kwargs={'noid': 'bogus', 'type': 'purl'})
        response = self.client.put(purl_uri, json.dumps(new),
                                   content_type='application/json', **ADMIN_AUTH)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s for PUT on %s (invalid pid), got %s" \
                % (expected, purl_uri, got))

        # not testing ark update separately because there are no logic differences from purl

    def test_search_pids(self):
        """
        Test the JSON return for searching pids.
        """
        # Set the base url to search all pids from.
        base_url = reverse('rest_api:search-pids')

        def _test_search_results(searchdict, expcount, expcode=200):
            # Tests status code for searches to ensure no errors.
            encoded_args = urllib.urlencode(searchdict)
            url = '%s?%s' % (base_url, encoded_args)
            response = self.client.get(url)
            expected, actual = expcode, response.status_code
            data = json.loads(response.content)
            self.failUnlessEqual(expected, actual, "Expected status code %s but returned %s for %s" % (expected, actual, url))
            if expcount is not 0:
                actcount = len(data['results'])
                self.failUnlessEqual(expcount, actcount, "Expected %s but found %s pids for query %s" % (expcount, actcount, url))

        # DEFAULT LIST RETURN
        _test_search_results({}, 3)

        # SIMPLE PID SEARCH
        # construct a simple search for a single pid.
        _test_search_results({'pid': '124tw'}, 1)

        # SIMPLE DOMAIN SEARCH
        # construct a simple domain search
        _test_search_results({'domain': 'lsdi'}, 1)
        # test again for case insensativity
        _test_search_results({'domain': 'LSDI'}, 1)

        # SIMPLE DOMAIN URI SEARCH
        _test_search_results({'domain_uri': 'http://pid.emory.edu/domains/2/'}, 1)

        # SIMPLE TARGET SEARCH
        _test_search_results({'target': 'http://domokun.library.emory.edu:8080/fedora/get/emory:8crx1/'}, 2)

        # TEST MULTIPLE VALUES
        _test_search_results({'domain': 'making of modern law', 'type': 'purl'}, 1)
        # this should return none
        _test_search_results({'domain': 'making of modern law', 'type': 'ark'}, 0)

        # TEST PAGING
        _test_search_results({'count': 1}, 1) # 3 total objects across 3 pages
        _test_search_results({'count': 2}, 2) # 3 total objects across 2 pages.
        _test_search_results({'count': 2, 'page': 2}, 1) # page 2 of above should have 1

        # Test various conditions where errors are expected instead of results.

        # Out of range page requests should return 404 Errors
        encoded_args = urllib.urlencode( {'count': 2, 'page': 200})
        url = '%s?%s' % (base_url, encoded_args)
        response = self.client.get(url)
        expected, actual = 404, response.status_code
        self.failUnlessEqual(expected, actual, "Expected status code %s but returned %s for %s" % (expected, actual, url))

        # Nonsense page reqeuests should return 404.
        encoded_args = urllib.urlencode( {'count': 2, 'page': 'toast'})
        url = '%s?%s' % (base_url, encoded_args)
        response = self.client.get(url)
        expected, actual = 404, response.status_code
        self.failUnlessEqual(expected, actual, "Expected status code %s but returned %s for %s" % (expected, actual, url))


    def test_update_pid_permissions(self):
        update_pid = reverse('rest_api:pid', kwargs={'noid': self.purl.pid, 'type': 'purl'})
        # test authorization

        # - no credentials
        response = self.client.put(update_pid, {})
        expected, got = 401, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (unauthorized) for %s with no credentials, got %s" \
                % (expected, update_pid, got))

        # - invalid credentials
        AUTH = auth_header('testuser', 'notmypassword')
        response = self.client.put(update_pid, {}, **AUTH)
        expected, got = 401, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (unauthorized) for %s with no credentials, got %s" \
                % (expected, update_pid, got))

        # - valid credentials but user doesn't have required permissions
        AUTH = auth_header(*user_credentials)
        response = self.client.put(update_pid, {}, **AUTH)
        expected, got = 403, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (forbidden) for %s as valid user with insufficent permissions, got %s" \
                % (expected, update_pid, got))

    def test_no_delete_pid(self):
        purl_uri = reverse('rest_api:pid', kwargs={'noid': self.purl.pid, 'type': 'purl'})

        response = self.client.delete(purl_uri)
        expected, got = 405, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (method not allowed) for DELETE on %s, got %s" \
                % (expected, purl_uri, got))
        self.assertContains(response, 'cannot be deleted', status_code=405)


    def test_update_target(self):
        # purl target
        target_uri = reverse('rest_api:purl-target', kwargs={'noid': self.purl.pid})
        new = {
            'proxy': '',
            'target_uri': 'http://foo.bar/',
            'active': False
        }
        response = self.client.put(target_uri, json.dumps(new),
                                   content_type='application/json', **ADMIN_AUTH)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (OK) for PUT on %s , got %s" \
                % (expected, target_uri, got))
        # should return updated target info
        expected, got = 'application/json', response['Content-Type']
        self.assertEqual(expected, got, "Expected Content-Type '%s' for PUT on %s, got '%s'" \
            % (expected, target_uri, got))
        data = json.loads(response.content)
        self.assert_(data, "Response content successfully loaded as JSON")
        self.assert_(data['uri'].endswith(target_uri),
                    "target resource URI present in response")

        pid = Pid.objects.get(pid=self.purl.pid)
        target = pid.primary_target()
        self.assertEqual(new['target_uri'], target.uri)
        self.assertEqual(None, target.proxy)
        self.assertEqual(new['active'], target.active)
        self.assertEqual('testadmin', target.pid.editor.username,
                        'Authenticated user is set as pid editor after updating target')

        # Test that log entries were created
        self.assertLogEntryForObject(target)
        self.assertLogEntryForObject(pid)


        # ark qualified target
        target_uri = reverse('rest_api:ark-target', kwargs={'noid': self.ark.pid,
                             'qualifier': 'PDF'})
        new = {
            'target_uri': 'http://foo.bar.baz/pdf'
        }
        response = self.client.put(target_uri, json.dumps(new),
                                   content_type='application/json', **ADMIN_AUTH)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (OK) for PUT on %s , got %s" \
                % (expected, target_uri, got))

        pid = Pid.objects.get(pid=self.ark.pid)
        target = pid.target_set.filter(qualify='PDF')[0]
        self.assertEqual(new['target_uri'], target.uri)

    def test_update_target_permissions(self):
        update_target = reverse('rest_api:purl-target', kwargs={'noid': self.purl.pid})
        # test authorization

        # - no credentials
        response = self.client.put(update_target, {})
        expected, got = 401, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (unauthorized) for %s with no credentials, got %s" \
                % (expected, update_target, got))

        # - invalid credentials
        AUTH = auth_header('testuser', 'notmypassword')
        response = self.client.put(update_target, {}, **AUTH)
        expected, got = 401, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (unauthorized) for %s with no credentials, got %s" \
                % (expected, update_target, got))

        # - valid credentials but user doesn't have required permissions
        AUTH = auth_header(*user_credentials)
        response = self.client.put(update_target, {}, **AUTH)
        expected, got = 403, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (forbidden) for %s as valid user with insufficent permissions, got %s" \
                % (expected, update_target, got))


    def test_create_target(self):
        # create a new ARK qualifier target
        target_uri = reverse('rest_api:ark-target', kwargs={'noid': self.ark.pid,
                             'qualifier': 'NEW'})
        new = {
            'target_uri': 'http://my.new.url/'
        }
        response = self.client.put(target_uri, json.dumps(new),
                                   content_type='application/json', **ADMIN_AUTH)
        expected, got = 201, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (Created) for PUT on %s (new qualifier), got %s" \
                % (expected, target_uri, got))
        # should return new target info
        expected, got = 'application/json', response['Content-Type']
        self.assertEqual(expected, got, "Expected Content-Type '%s' for PUT on %s, got '%s'" \
            % (expected, target_uri, got))
        data = json.loads(response.content)
        self.assert_(data, "Response content successfully loaded as JSON")
        self.assert_(data['uri'].endswith(target_uri),
                    "target resource URI present in response")

        pid = Pid.objects.get(pid=self.ark.pid)
        # ARK fixture has 2 targets - there should now be 3
        self.assertEqual(3, pid.target_set.count())
        target = pid.target_set.filter(qualify='NEW')[0]
        self.assertEqual(new['target_uri'], target.uri)

        # url definitions do not allow qualified targets on purls
        # url pattern rules out invalid qualifier characters

        # nonexistent noid - should 404
        target_uri = reverse('rest_api:ark-target', kwargs={'noid': 'bogus',
                             'qualifier': 'NEW'})
        new = {
            'target_uri': 'http://my.new.url/'
        }
        response = self.client.put(target_uri, json.dumps(new),
                                   content_type='application/json', **ADMIN_AUTH)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (not found) for PUT on %s (nonexistent pid), got %s" \
                % (expected, target_uri, got))

    def test_delete_target(self):
        # PURL target can't be deleted
        purl_target = reverse('rest_api:purl-target', kwargs={'noid': self.purl.pid})
        response = self.client.delete(purl_target, **ADMIN_AUTH)
        expected, got = 405, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (method not allowed) for DELETE on %s, got %s" \
                % (expected, purl_target, got))
        self.assert_('DELETE' not in response['Allow'],
                'DELETE response for PURL should not list DELETE in allowed methods')

        # ARK target *can* be deleted
        # - qualified ARK target
        # store reference to target object in order to test log entry creation
        target = self.ark.target_set.filter(qualify='PDF')[0]
        target_uri = reverse('rest_api:ark-target', kwargs={'noid': self.ark.pid,
                             'qualifier': 'PDF'})
        response = self.client.delete(target_uri, **ADMIN_AUTH)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (OK) for DELETE on %s, got %s" \
                % (expected, target_uri, got))
        self.assertEqual(0, self.ark.target_set.filter(qualify='PDF').count(),
            'Qualified PDF target should not be present in ARK target set after delete')

        # test logging
        self.assertLogEntryForObject(self.ark)
        self.assertLogEntryForObject(target)

        # - unqualfied ARK target
        target_uri = reverse('rest_api:ark-target', kwargs={'noid': self.ark.pid,
                             'qualifier': ''})
        response = self.client.delete(target_uri, **ADMIN_AUTH)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (OK) for DELETE on %s, got %s" \
                % (expected, target_uri, got))
        self.assertEqual(0, self.ark.target_set.filter(qualify='').count(),
            'Unqualified target no longer present in ARK target set after delete')

        # POST not supported for target - use that to check 405 response
        response = self.client.post(target_uri, **ADMIN_AUTH)
        # delete *should* be listed in allowed methods for ARK targets
        self.assert_('DELETE' in response['Allow'],
                'DELETE response for PURL should not list DELETE in allowed methods')

        # delete on non-existent target should 404
        target_uri = reverse('rest_api:ark-target', kwargs={'noid': self.ark.pid,
                             'qualifier': 'not-really-here'})
        response = self.client.delete(target_uri, **ADMIN_AUTH)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (OK) for DELETE on %s (nonexistent target), got %s" \
                % (expected, target_uri, got))

    def test_delete_target_permissions(self):
        target_uri = reverse('rest_api:ark-target', kwargs={'noid': self.ark.pid,
                             'qualifier': 'PDF'})
        # - no credentials
        response = self.client.delete(target_uri, {})
        expected, got = 401, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (unauthorized) for DELETE on %s with no credentials, got %s" \
                % (expected, target_uri, got))

        # - invalid credentials
        AUTH = auth_header('testuser', 'notmypassword')
        response = self.client.put(target_uri, {}, **AUTH)
        expected, got = 401, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (unauthorized) for DELETE on %s with no credentials, got %s" \
                % (expected, target_uri, got))

        # - valid credentials but user doesn't have required permissions
        AUTH = auth_header(*user_credentials)
        response = self.client.put(target_uri, {}, **AUTH)
        expected, got = 403, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (forbidden) for DELETE on %s as valid user with insufficent permissions, got %s" \
                % (expected, target_uri, got))

    def test_list_domains(self):
        domains_url = reverse('rest_api:domains')
        response = self.client.get(domains_url)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got, "Expected status code %s for %s, got %s" \
                % (expected, domains_url, got))
        expected, got = 'application/json', response['Content-Type']
        self.assertEqual(expected, got, "Expected Content-Type '%s' for GET on %s, got '%s'" \
            % (expected, domains_url, got))
        data = json.loads(response.content)
        self.assert_(data, "List domains response content successfully loaded as JSON")
        domain_names = [d['name'] for d in data]

        # response should list top-level domains
        # (any subdomains are included under their parent domain)
        top_level_domains = Domain.objects.filter(parent=None)
        for d in top_level_domains:
            self.assert_(d.name in domain_names,
                'top-level domain %s should be listed in list domains response' % d.name)
        subdomains = Domain.objects.filter(parent__isnull=False)
        for sd in subdomains:
            self.assert_(sd.name not in domain_names,
                'subdomain %s should be listed in top-level list domains response' % sd.name)

        # PUT - not allowed
        response = self.client.put(domains_url)
        expected, got = 405, response.status_code
        self.assertEqual(expected, got,
                "Expected status code %s (method not allowed) for PUT to %s, got %s" \
                % (expected, domains_url, got))
        self.assert_('GET' in response['Allow'],
                'PUT response should list GET in allowed methods')

    def test_get_domain(self):
        domain_url = reverse('rest_api:domain', kwargs={'id': 1})
        response = self.client.get(domain_url)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got, "Expected status code %s for %s, got %s" \
                % (expected, domain_url, got))
        expected, got = 'application/json', response['Content-Type']
        self.assertEqual(expected, got, "Expected Content-Type '%s' for GET on %s, got '%s'" \
            % (expected, domain_url, got))
        data = json.loads(response.content)
        self.assert_(data, "Single domain response content successfully loaded as JSON")
        # domain data conversion is tested elsewhere

        domain_url = reverse('rest_api:domain', kwargs={'id': 3030})
        response = self.client.get(domain_url)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got, "Expected status code %s for %s (bad id), got %s" \
                % (expected, domain_url, got))


    def test_create_domain(self):
        #Unless specified, tests are with a user with  sufficient permissions
        domain_url = reverse('rest_api:domains')

        parent_id = 1
        # parent uri
        domain_uri_parent = 'http://testserver' + reverse('rest_api:domain', kwargs={'id' : parent_id})
        # invalid parent
        domain_uri_bad = 'http://testserver' + reverse('rest_api:domain', kwargs={'id': 100})

        # delete is not allowed
        response = self.client.delete(domain_url, **ADMIN_AUTH)
        expected, got = 405, response.status_code
        self.assertEqual(expected, got, "Expected status code %s (method not allowed) for DELETE to %s, got %s" \
                % (expected, domain_url, got))

        #name is required in post data
        response = self.client.post(domain_url, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s for post to %s, got %s" \
                % (expected, domain_url, got))
        expected, got = "Error: name is required", response.content
        self.assertEqual(expected, got, "Expected %s got %s" % (expected, got))

        # name exists but is blank
        data = {"name" : ""}
        response = self.client.post(domain_url, data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" % (expected, got))
        expected, got = "Error: name is required", response.content
        self.assertEqual(expected, got, "Expected %s got %s" % (expected, got))

        # name exists but is None
        data = {"name" : None}
        response = self.client.post(domain_url, data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" % (expected, got))
        expected, got = "Error: name is required", response.content
        self.assertEqual(expected, got, "Expected %s got %s" % (expected, got))

        # duplicate name can not be created even if policy and  parent changes
        data = {"name" : "LSDI", 'policy' :"Not Guaranteed", 'parent' : domain_uri_parent}
        response = self.client.post(domain_url, data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" % (expected, got))
        expected, got = "Error: Domain '%s' already exists" % (data['name']), response.content
        self.assertEqual(expected, got, "Expected %s got %s" % (expected, got))

        # Try to create Domain with exactly the same values as an existing Domain - Should return 400
        response = self.client.post(domain_url, {"name" : "LSDI", "policy" : "Permanent, Stable Content"}, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" % (expected, got))
        expected, got = "Error: Domain '%s' already exists" % (data['name']), response.content
        self.assertEqual(expected, got, "Expected %s got %s" % (expected, got))

        # invalid parent
        response = self.client.post(domain_url, {"name" : "New Domain 1", "parent" : domain_uri_bad}, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" % (expected, got))
        expected, got = "Error: Parent %s does not exists" % (domain_uri_bad), response.content
        self.assertEqual(expected, got, "Expected %s got %s" % (expected, got))

        #invalid policy
        data = {"name" : "New Domain 2", "policy" : "BAD POLICY"}
        response = self.client.post(domain_url, data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" % (expected, got))
        expected, got = "Error: Policy %s does not exists" % (data['policy']), response.content
        self.assertEqual(expected, got, "Expected %s got %s" % (expected, got))

        # create a new domain
        data = {"name" : "New Test Domain", "policy" : "Not Guaranteed", "parent" : domain_uri_parent}
        response = self.client.post(domain_url, data, **ADMIN_AUTH)
        expected, got = 201, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" % (expected, got))
        # should return the uri of the newly-created domain
        d = _domain_from_uri(response.content)
        self.assert_(isinstance(d, Domain))
        #make sure it was created with correct fields set
        self.assertEquals(parent_id, d.parent.id) #get the id from the uri and compare
        self.assertEqual(data['policy'], d.policy.title)

        # Test that log entry was created
        self.assertLogEntryForObject(d)

        # Try creating the "New Test" Doman again - Should return 400
        response = self.client.post(domain_url, data, **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" % (expected, got))
        expected, got = "Error: Domain '%s' already exists" % (data['name']), response.content
        self.assertEqual(expected, got, "Expected %s got %s" % (expected, got))

        # no credentials
        response = self.client.post(domain_url, {"name" : "New Test Domain 2"})
        expected, got = 401, response.status_code
        self.assertEqual(expected, got, "Expected status code %s because no user /pass was in post  got %s" % (expected, got))

        # invalid credentials
        AUTH = auth_header('testuser', 'notmypassword')
        response = self.client.post(domain_url, {"name" : "New Test Domain 2"}, **AUTH)
        expected, got = 401, response.status_code
        self.assertEqual(expected, got, "Expected status code %s because of invalid user / pass got %s" % (expected, got))


        # valid credentials but action not allowed
        AUTH = auth_header(*user_credentials)
        response = self.client.post(domain_url, {"name" : "New Test Domain 2"}, **AUTH)
        expected, got = 403, response.status_code
        self.assertEqual(expected, got, "Expected status code %s because user is not allowed to create a Domain got %s" % (expected, got))

    def test_update_domain(self):
        # Unless specified, tests are with a user with  sufficient permissions
        domain_url = 'http://testserver' + reverse('rest_api:domain', kwargs={"id" : 1}) # This uri exists and should be used for testing
        domain_url_parent = 'http://testserver' + reverse('rest_api:domain', kwargs={"id" : 2}) # This uri exists and should be used for testing the parent Domain
        domain_url_bad = 'http://testserver' + reverse('rest_api:domain', kwargs={"id" : 100})  #This uri does not exist

        # DELETE is not allowed
        response = self.client.delete(domain_url)
        expected, got = 405, response.status_code
        self.assertEqual(expected, got, "Expected status code %s (method not allowed) for DELETE to %s, got %s" \
                % (expected, domain_url, got))

        # POST is not allowed
        response = self.client.post(domain_url)
        expected, got = 405, response.status_code
        self.assertEqual(expected, got, "Expected status code %s (method not allowed) for POST to %s, got %s" \
                % (expected, domain_url, got))

        # PUT with correct content type but trying to update Doman that does not exist
        response = self.client.put(domain_url_bad, json.dumps({}), content_type='application/json')
        expected, got = 404, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s  - Domain does not exist" \
                % (expected, got))

        # PUT with wrong content type
        response = self.client.put(domain_url, '', CONTENT_TYPE='text/plain', **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" \
                % (expected, got))
        expected, got = "Error: Unsupported content type 'text/plain'; please use a supported format: application/json", response.content
        self.assertEqual(expected, got, "Expected %s got %s" \
                % (expected, got))

        # PUT with correct content type but no JSON data
        response = self.client.put(domain_url, json.dumps({}), content_type='application/json', **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s - no JSON data passed" \
                % (expected, got))
        expected, got = "Error: No Parameters Passed", response.content
        self.assertEqual(expected, got, "Expected  %s got %s" \
                % (expected, got))

        # PUT with invalid parent
        data = {'name' : "New Name", 'parent' : domain_url_bad, 'policy' : "Permanent, Stable Content"}
        response = self.client.put(domain_url, json.dumps(data), content_type='application/json', **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s - invalid parent uri" \
                % (expected, got))
        expected, got = "Error: Could not find Domain for URI %s" % (domain_url_bad), response.content
        self.assertEqual(expected, got, "Expected  %s got %s" \
                % (expected, got))

        # PUT with invalid policy
        data = {'name' : "New Name", 'parent' : domain_url_parent, 'policy' : "Bad Policy"}
        response = self.client.put(domain_url, json.dumps(data), content_type='application/json', **ADMIN_AUTH)
        expected, got = 400, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s - invalid policy" \
                % (expected, got))
        expected, got = "Error: Policy '%s' not found" % (data['policy']), response.content
        self.assertEqual(expected, got, "Expected  %s got %s" \
                % (expected, got))

        # PUT valid data
        data = {'name' : "New Name", 'parent' : domain_url_parent, 'policy' : "Permanent, Stable Content"}
        response = self.client.put(domain_url, json.dumps(data), content_type='application/json', **ADMIN_AUTH)
        expected, got = 200, response.status_code
        self.assertEqual(expected, got, "Expected status code %s got %s" \
                % (expected, got))

        # check the values in the DB
        parent_id = int(data['parent'].split('/')[4])
        d = Domain.objects.get(id=1)
        self.assertEqual(d.name, data['name']);
        self.assertEqual(d.parent.id, parent_id) # get parent id from uri and compare
        self.assertEqual(d.policy.title, data['policy']);

        # Check the values in the JSON object that is returned
        obj = json.loads(response.content)
        self.assertEqual(obj['name'], data['name']);
        self.assertEqual(obj['policy'], data['policy']);
        self.assertEqual(obj['domain'], data['parent'])

        # check for log entry
        self.assertLogEntryForObject(d)

        # no credentials
        response = self.client.put(domain_url, {"name" : "New Test Domain 2"})
        expected, got = 401, response.status_code
        self.assertEqual(expected, got, "Expected status code %s because no user /pass was in post  got %s" % (expected, got))

        # invalid credentials
        AUTH = auth_header('testuser', 'notmypassword')
        response = self.client.put(domain_url, {"name" : "New Test Domain 2"}, **AUTH)
        expected, got = 401, response.status_code
        self.assertEqual(expected, got, "Expected status code %s because of invalid user / pass got %s" % (expected, got))

        # valid credentials but action not allowed
        AUTH = auth_header(*user_credentials)
        response = self.client.put(domain_url, {"name" : "New Test Domain 2"}, **AUTH)
        expected, got = 403, response.status_code
        self.assertEqual(expected, got, "Expected status code %s because user is not allowed to create a Domain got %s" % (expected, got))


    # *** utility methods ***

    def test_pid_data(self):
        data = pid_data(self.purl, self.request)
        self.assert_('name' not in data,
            'name not included in pid data when pid name is blank')
        # this purl has an explicit policy
        data = pid_data(self.inactive_purl, self.request)
        self.assertEqual(self.inactive_purl.policy.title, data['policy'],
            'policy listed by title in pid data when pid has a policy')
        self.assertEqual('testuser', data['creator'],
            'creator listed by username and not db id')
        self.assertEqual('testuser', data['editor'],
            'editor listed by username and not db id')
        self.assertEqual('EUCLID', data['external_system']['id'],
            'external system listed by system name and not db id')
        # confirm dates are ISO format

        self.assert_(self.isodate_re.match(data['created']),
            "date created should be in ISO format - %s should match regular expression %s" %\
            (data['created'], self.isodate_re.pattern))
        self.assert_(self.isodate_re.match(data['updated']),
            "date created should be in ISO format - %s should match regular expression %s" %\
            ( data['updated'], self.isodate_re.pattern))

        data = pid_data(self.ark, self.request)
        self.assert_('external_system' not in data,
            'external system is not included in pid data when blank')
        self.assert_('policy' not in data,
            'policy not included in pid data when pid has no policy')



    def test_target_data(self):
        data = target_data(self.purl.primary_target(), self.request)
        self.assertEqual('EZproxy', data['proxy'],
                'Target proxy is listed in data by name')
        self.assertEqual(True, data['active'])

        data = target_data(self.inactive_purl.primary_target(), self.request)
        self.assertEqual(False, data['active'])

    def test_domain_data(self):
        # domain with no subdomains
        lsdi = Domain.objects.get(name='LSDI')
        data = domain_data(lsdi, self.request)
        self.assertEqual('Permanent, Stable Content', data['policy'],
                'Domain policy is listed in data by title')
        self.assert_(self.isodate_re.match(data['updated']),
            'date updated should be in ISO format - %s should match regular expression %s' %\
            (data['updated'], self.isodate_re.pattern))
        self.assert_('number of pids' in data,
            'data should include number of pids in this domain')
        domain_url = reverse('rest_api:domain', kwargs={'id': lsdi.id})
        self.assert_(data['uri'].endswith(domain_url),
            'domain resource URI present in data')
        self.assert_('collections' not in data,
            'domain with no subdomains should not have collections listed in data')

        # domain with subdomain
        gencoll = Domain.objects.get(name='General purchased collections')
        data = domain_data(gencoll, self.request)
        self.assert_(data['collections'],
            'domain with subdomains should have collections listed in data')

        # subdomain
        subdomain = gencoll.collections.all()[0]
        data = domain_data(subdomain, self.request)
        domain_url = reverse('rest_api:domain', kwargs={'id': gencoll.id})
        self.assert_(data['domain'].endswith(domain_url),
            'parent domain resource URI is included in data for a subdomain')
