from django.test import TestCase, TransactionTestCase
from pidman.usage_stats.models import *
from pidman.pid.models import Target
from pidman.usage_stats.management.commands.parse_access_log import Command

class TestTargetAccessLog(TestCase):
    fixtures = ['usage_stats_pids.json']

    def test_init_ARK(self):
		log = createTargetAccessLog(noid='rkx', qualifier='discoverE',
            ip='170.140.215.175', timestamp='19/Aug/2009:11:29:14 -0400', referrer=None,
            browser='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2')
		self.failUnless(isinstance(log, TargetAccessLog))

		l = TargetAccessLog.objects.get(pk=log.id)
		self.assertEquals(l, log)

		t = Target.objects.get(noid='rkx', qualify='discoverE')
		self.assertEquals(log.target, t)

    def test_init_no_qualifier(self):
        log = createTargetAccessLog(noid='rkx',
            ip='170.140.215.175', timestamp='19/Aug/2009:11:29:15 -0400', referrer=None,
            browser='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2')

        self.failUnless(isinstance(log, TargetAccessLog))

        l = TargetAccessLog.objects.get(pk=log.id)
        self.assertEquals(l, log)

        t = Target.objects.get(noid='rkx', qualify="")
        self.assertEquals(log.target, t)

    def test_init_empty_qualifier(self):
        log = createTargetAccessLog(noid='rkx', qualifier='',
            ip='170.140.215.175', timestamp='19/Aug/2009:11:29:16 -0400', referrer=None,
            browser='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2')

        self.failUnless(isinstance(log, TargetAccessLog))

        l = TargetAccessLog.objects.get(pk=log.id)
        self.assertEquals(l, log)

        t = Target.objects.get(noid='rkx', qualify="")
        self.assertEquals(log.target, t)

    def test_init_null_qualifier(self):
        log = createTargetAccessLog(noid='rkx', qualifier="",
            ip='170.140.215.175', timestamp='19/Aug/2009:11:29:17 -0400', referrer=None,
            browser='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2')

        self.failUnless(isinstance(log, TargetAccessLog))

        l = TargetAccessLog.objects.get(pk=log.id)
        self.assertEquals(l, log)

        t = Target.objects.get(noid='rkx', qualify="")
        self.assertEquals(log.target, t)

class TestDup(TransactionTestCase):
    #requires TransactionTestCase
    fixtures = ['usage_stats_pids.json']
    def test_dup(self):
        createTargetAccessLog(noid='rkx', qualifier='discoverE',
            ip='170.140.215.175', timestamp='19/Aug/2009:11:29:18 -0400', referrer=None,
            browser='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2')

        createTargetAccessLog(noid='rkx', qualifier='discoverE',
            ip='170.140.215.175', timestamp='19/Aug/2009:11:29:18 -0400', referrer=None,
            browser='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2')

        t = Target.objects.get(noid='rkx', qualify='discoverE')
        self.assertEquals(len(t.targetaccesslog_set.all()), 1)

class TestParseCommand(TestCase):
    def setUp(self):
        self.command = Command()

    def test_parse_purl(self):
        line = '170.140.211.29 - - [03/Sep/2009:13:44:24 -0400] "GET /7qpi HTTP/1.1" 302 112 "-" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2"'

        result = self.command.parse(line)
        self.assertEquals(result['ip'], '170.140.211.29')
        self.assertEquals(result['noid'], '7qpi')
        self.assertEquals(result['qualifier'], None)
        self.assertEquals(result['timestamp'], '03/Sep/2009:13:44:24 -0400')
        self.assertEquals(result['request'], 'GET /7qpi HTTP/1.1')
        self.assertEquals(result['browser'], 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2')
        self.assertEquals(result['user'], None)
        self.assertEquals(result['referrer'], None)

    def test_parse_ark(self):
        line = '170.140.211.29 - - [03/Sep/2009:13:17:33 -0400] "GET /ark:/25593/16x4s/POD HTTP/1.1" 302 85 "-" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2"'

        result = self.command.parse(line)
        self.assertEquals(result['ip'], '170.140.211.29')
        self.assertEquals(result['noid'], '16x4s')
        self.assertEquals(result['qualifier'], 'POD')
        self.assertEquals(result['timestamp'], '03/Sep/2009:13:17:33 -0400')
        self.assertEquals(result['request'], 'GET /ark:/25593/16x4s/POD HTTP/1.1')
        self.assertEquals(result['browser'], 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2')
        self.assertEquals(result['user'], None)
        self.assertEquals(result['referrer'], None)

    def test_exclude_resolver_lines(self):
        line = '170.140.223.79 - - [03/Sep/2009:13:12:43 -0400] "GET /resolver/resolver/handler?query=ark:/25593/159g7 HTTP/1.1" 302 107 "-" "check_http/1.81 (nagios-plugins 1.4)"'
        result = self.command.parse(line)
        self.assertEquals(result, None)

    def test_exclude_robot_lines(self):
        line = '65.55.207.25 - - [03/Sep/2009:13:25:43 -0400] "GET /robots.txt HTTP/1.1" 404 1724 "-" "msnbot/2.0b (+http://search.msn.com/msnbot.htm)"'
        result = self.command.parse(line)
        self.assertEquals(result, None)

    def test_exclude_ip_lines(self):
        line = '170.140.223.57 - - [03/Sep/2009:13:27:43 -0400] "GET /ark:/25593/159g7 HTTP/1.0" 302 107 "-" "check_http/1.81 (nagios-plugins 1.4)"'
        result = self.command.parse(line)
        self.assertEquals(result, None)

    def test_exclude_browser_agents(self):
        line = '66.249.67.88 - - [03/Sep/2009:13:07:28 -0400] "GET /ark:/25593/1778b HTTP/1.1" 302 106 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"'
        result = self.command.parse(line)
        self.assertEquals(result, None)

        line = '66.235.124.19 - - [03/Sep/2009:13:16:00 -0400] "GET /ark:/25593/15h0x HTTP/1.1" 302 106 "-" "Mozilla/5.0 (compatible; Ask Jeeves/Teoma; +http://about.ask.com/en/docs/about/webmasters.shtml)"'
        result = self.command.parse(line)
        self.assertEquals(result, None)

class TestFiscalYear(TestCase):
    fixtures = ['log.json']

    def test_fiscal_years(self):
        fyears = [2007, 2008, 2009]
        self.assertEquals(fiscal_years(), fyears)

    def test_get_by_fiscal_year(self):
        self.assertEquals(len(get_by_fiscal_year(2009)), 51)
        self.assertEquals(len(get_by_fiscal_year(2008)), 2)
        self.assertEquals(len(get_by_fiscal_year(2007)), 2)
